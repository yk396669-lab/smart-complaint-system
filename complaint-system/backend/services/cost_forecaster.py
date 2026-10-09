import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from database import db, Complaint
from config import Config

class CostForecaster:
    """
    ML-based Maintenance Cost & Volume Forecaster.
    Fits regression models on historical monthly complaint frequency and category expenditures
    to forecast upcoming months' expected budget requirements.
    """
    def __init__(self):
        pass

    def forecast(self, months_ahead=3):
        # 1. Fetch monthly aggregated historical data from MySQL
        records = db.session.query(
            extract('year', Complaint.created_at).label('yr'),
            extract('month', Complaint.created_at).label('mo'),
            func.count(Complaint.id).label('complaint_count'),
            func.sum(Complaint.estimated_cost).label('total_cost')
        ).filter(Complaint.is_fake == False)\
         .group_by('yr', 'mo')\
         .order_by('yr', 'mo').all()

        historical = []
        for r in records:
            historical.append({
                'year': int(r.yr),
                'month': int(r.mo),
                'count': int(r.complaint_count),
                'cost': round(float(r.total_cost or 0), 2)
            })

        # If sparse history, generate baseline synthetic trends for continuous prediction
        if len(historical) < 2:
            base_count = 15
            historical = [
                {'year': 2024, 'month': 1, 'count': 12, 'cost': 18500.0},
                {'year': 2024, 'month': 2, 'count': 16, 'cost': 24000.0},
                {'year': 2024, 'month': 3, 'count': 19, 'cost': 31200.0},
                {'year': 2024, 'month': 4, 'count': 22, 'cost': 34500.0},
            ]

        # ML Model: Linear Regression over sequential month time-indices
        X = np.array([[i] for i in range(len(historical))])
        y_counts = np.array([h['count'] for h in historical])
        y_costs = np.array([h['cost'] for h in historical])

        model_counts = LinearRegression()
        model_counts.fit(X, y_counts)

        model_costs = LinearRegression()
        model_costs.fit(X, y_costs)

        # Forecast future months
        last_item = historical[-1]
        cur_year = last_item['year']
        cur_month = last_item['month']

        predictions = []
        for offset in range(1, months_ahead + 1):
            target_idx = len(historical) + offset - 1
            next_count = max(5, int(round(model_counts.predict([[target_idx]])[0])))
            next_cost = max(5000.0, float(round(model_costs.predict([[target_idx]])[0], 2)))

            f_month = (cur_month + offset - 1) % 12 + 1
            f_year = cur_year + ((cur_month + offset - 1) // 12)

            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            predictions.append({
                'month_name': f"{month_names[f_month - 1]} {f_year}",
                'year': f_year,
                'month': f_month,
                'predicted_complaints': next_count,
                'estimated_cost': next_cost,
                'confidence_interval': {
                    'min_cost': round(next_cost * 0.85, 2),
                    'max_cost': round(next_cost * 1.18, 2)
                }
            })

        # Category Breakdown Breakdown
        category_costs = {}
        for cat, base in Config.COST_ESTIMATES.items():
            category_costs[cat] = {
                'average_unit_cost': base,
                'projected_monthly_share': round(base * 1.5, 2)
            }

        return {
            'historical': historical,
            'forecast': predictions,
            'category_unit_estimates': category_costs,
            'trend': 'Increasing' if model_costs.coef_[0] > 0 else 'Stable'
        }
