from sqlalchemy import func
from database import db, Complaint

class HotspotAnalyzer:
    """
    Computes geographical hotspot clusters and vulnerability scores
    across hostel blocks and campus facilities.
    """
    DEFAULT_COORDINATES = {
        'Hostel A': {'lat': 17.2535, 'lng': 78.4312},
        'Hostel B': {'lat': 17.2518, 'lng': 78.4335},
        'Hostel C': {'lat': 17.2495, 'lng': 78.4288},
        'Hostel D': {'lat': 17.2548, 'lng': 78.4350},
        'Dining Hall': {'lat': 17.2515, 'lng': 78.4310},
        'Sports Complex': {'lat': 17.2550, 'lng': 78.4290},
        'Library Block': {'lat': 17.2505, 'lng': 78.4340},
    }

    SEVERITY_WEIGHTS = {
        'Critical': 4.0,
        'High': 3.0,
        'Medium': 2.0,
        'Low': 1.0
    }

    def analyze(self):
        complaints = Complaint.query.filter(Complaint.is_fake == False).all()

        hostel_stats = {}
        for c in complaints:
            h = c.hostel or 'Unassigned'
            if h not in hostel_stats:
                coords = self.DEFAULT_COORDINATES.get(h, {'lat': 12.9720, 'lng': 77.5950})
                hostel_stats[h] = {
                    'hostel': h,
                    'total_complaints': 0,
                    'open_complaints': 0,
                    'resolved_complaints': 0,
                    'repeat_complaints': 0,
                    'weighted_severity_score': 0.0,
                    'categories': {},
                    'latitude': c.latitude or coords['lat'],
                    'longitude': c.longitude or coords['lng'],
                }

            s = hostel_stats[h]
            s['total_complaints'] += 1
            if c.status in ['Open', 'In Progress']:
                s['open_complaints'] += 1
            elif c.status == 'Resolved':
                s['resolved_complaints'] += 1

            if c.is_repeat:
                s['repeat_complaints'] += 1

            w = self.SEVERITY_WEIGHTS.get(c.severity, 2.0)
            s['weighted_severity_score'] += w

            s['categories'][c.category] = s['categories'].get(c.category, 0) + 1

        # Calculate normalized risk index (0 to 100)
        hotspot_list = []
        for h, d in hostel_stats.items():
            tot = d['total_complaints']
            open_ratio = (d['open_complaints'] / max(1, tot))
            # Composite risk formula
            risk_raw = (d['weighted_severity_score'] * 1.5) + (open_ratio * 30.0) + (d['repeat_complaints'] * 5.0)
            risk_score = min(100, int(round(risk_raw)))

            if risk_score >= 70:
                risk_level = 'High Risk'
                color = '#f44336' # Red
            elif risk_score >= 40:
                risk_level = 'Medium Risk'
                color = '#ff9800' # Orange
            else:
                risk_level = 'Low Risk'
                color = '#4caf50' # Green

            # Top offending category
            top_category = max(d['categories'].items(), key=lambda x: x[1])[0] if d['categories'] else 'General'

            hotspot_list.append({
                'hostel': h,
                'total_complaints': d['total_complaints'],
                'open_complaints': d['open_complaints'],
                'repeat_complaints': d['repeat_complaints'],
                'risk_score': risk_score,
                'risk_level': risk_level,
                'color': color,
                'top_category': top_category,
                'latitude': d['latitude'],
                'longitude': d['longitude'],
                'category_breakdown': d['categories']
            })

        hotspot_list.sort(key=lambda x: x['risk_score'], reverse=True)
        return hotspot_list
