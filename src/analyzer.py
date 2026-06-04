def score_ratio(value: float, low: float, mid: float, high: float, lower_is_better: bool = False) -> int:
    """Generic scoring helper logic for single numerical metrics."""
    if value is None or value == 0:
        return 0
        
    if lower_is_better:
        if value <= low:  return 2
        if value <= mid:  return 1
        return 0
    else:
        if value >= high: return 2
        if value >= mid:  return 1
        return 0

def overall_score(ratios: dict) -> dict:
    """
    Maps specific dictionary keys from ratios.py to group health scores.
    Aggregates metrics and returns total points and an investment grade.
    """
    # Defensive scalar unpacker helper function
    def unpack(key, default=0.0):
        val = ratios.get(key, default)
        if hasattr(val, "iloc"):
            return val.iloc[0] if not val.empty else default
        return val

    # Extract required metric items explicitly
    net_margin     = unpack("net_margin")
    roe            = unpack("roe")
    current_ratio  = unpack("current_ratio")
    debt_to_equity = unpack("debt_to_equity")
    pe_ratio       = unpack("pe_ratio")

    # 1. Compile the core category scoring map dictionary
    scores = {
        "profitability": score_ratio(net_margin,     5.0,  15.0, 25.0), 
        "roe":           score_ratio(roe,            8.0,  14.0, 20.0), 
        "liquidity":     score_ratio(current_ratio,  1.0,  1.5,  2.0),  
        "leverage":      score_ratio(debt_to_equity, 0.5, 1.0, 2.0, lower_is_better=True), 
        "valuation":     score_ratio(pe_ratio, 15.0, 20.0, 30.0, lower_is_better=True) 
    }

    # 2. FIX: Automatically calculate raw point totals (Maximum possible points: 10)
    total_score = sum(scores.values())

    # 3. Assign an explicit executive credit investment grade label
    if total_score >= 8:
        grade = "Strong"
    elif total_score >= 5:
        grade = "Fair"
    else:
        grade = "Weak"

    # 4. Merge dictionaries together using the unpacking operator (**)
    return {
        **scores,
        "_total_score": total_score,
        "_final_grade": grade
    }