# src/analysis/risk_profiler.py
def get_risk_level(coin, risk_tolerance):
    conservative = ["Bitcoin", "Ethereum"]
    base_score = 1 if coin in conservative else 2

    tolerance_map = {
        "Very Low": 0,
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Very High": 4
    }

    level = base_score + tolerance_map.get(risk_tolerance, 2)
    return ["Very Low", "Low", "Medium", "High", "Very High"][min(level, 4)]
