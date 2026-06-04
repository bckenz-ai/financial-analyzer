"""
Standardizes all index keys by forcing them to lowercase and removing spaces, then implements 
fallback search keys so it never fails to pull a line item again.
"""

import pandas as pd

def safe_lookup(df, keywords: list):
    """
    Defensively searches a DataFrame index using normalized string matches 
    to handle variable naming shifts on Yahoo Finance.
    """
    # Standardize the index: lowercase and strip spaces
    normalized_index = df.index.astype(str).str.lower().str.replace(" ", "").str.replace("_", "")
    
    for kw in keywords:
        clean_kw = kw.lower().replace(" ", "").replace("_", "")
        if clean_kw in normalized_index.values:
            # Find the actual original index label position
            idx_position = normalized_index.get_loc(clean_kw)
            # If the index location is a boolean mask, pick the first match
            if isinstance(idx_position, int):
                return df.iloc[idx_position]
            else:
                return df.iloc[idx_position].iloc[0]
                
    # Fallback to a row of zeros matching the column width if completely missing
    return pd.Series(0.0, index=df.columns)

def profitability(inc, bal):
    """Computes operational profitability margins defensively by normalizing date indexes."""
    # 1. Standardize column date formats to clean strings (YYYY-MM-DD)
    # This prevents pandas from failing to align mismatched datetime structures
    inc_clean = inc.copy()
    bal_clean = bal.copy()
    
    inc_clean.columns = pd.to_datetime(inc_clean.columns).strftime('%Y-%m-%d')
    bal_clean.columns = pd.to_datetime(bal_clean.columns).strftime('%Y-%m-%d')

    # 2. Perform safe lookups using our normalized copies
    rev    = safe_lookup(inc_clean, ["Total Revenue", "TotalRevenue", "Operating Revenue"])
    gp     = safe_lookup(inc_clean, ["Gross Profit", "GrossProfit"])
    ni     = safe_lookup(inc_clean, ["Net Income", "NetIncome", "Net Income Common Stockholders"])
    ebitda = safe_lookup(inc_clean, ["EBITDA"])
    
    equity = safe_lookup(bal_clean, ["Stockholders Equity", "StockholdersEquity", "Total Equity Gross Minority Interest"])
    assets = safe_lookup(bal_clean, ["Total Assets", "TotalAssets"])
    
    # 3. Compute baseline metrics
    gross_margin  = (gp / rev * 100).round(2).fillna(0)
    net_margin    = (ni / rev * 100).round(2).fillna(0)
    ebitda_margin = (ebitda / rev * 100).round(2).fillna(0)
    
    # 4. Safely calculate cross-statement ratios using explicit date mapping
    # If shapes still don't align, clip the data to the matching available years
    common_dates = inc_clean.columns.intersection(bal_clean.columns)
    
    if not common_dates.empty:
        roe = (ni[common_dates] / equity[common_dates] * 100).round(2).fillna(0)
        roa = (ni[common_dates] / assets[common_dates] * 100).round(2).fillna(0)
    else:
        # Emergency backup: If dates still conflict, align purely by sequence position
        min_len = min(len(ni), len(equity))
        roe = pd.Series((ni.iloc[:min_len].values / equity.iloc[:min_len].values * 100).round(2), index=ni.index[:min_len]).fillna(0)
        roa = pd.Series((ni.iloc[:min_len].values / assets.iloc[:min_len].values * 100).round(2), index=ni.index[:min_len]).fillna(0)
    
    return {
        "gross_margin":   gross_margin,
        "net_margin":     net_margin,
        "ebitda_margin":  ebitda_margin,
        "roe":            roe,   
        "roa":            roa,   
    }

def liquidity_solvency(bal):
    """Computes solvency capability metrics cleanly."""
    ca  = safe_lookup(bal, ["Current Assets", "CurrentAssets", "Total Current Assets"])
    cl  = safe_lookup(bal, ["Current Liabilities", "CurrentLiabilities", "Total Current Liabilities"])
    inv = safe_lookup(bal, ["Inventory", "Inventories"])
    td  = safe_lookup(bal, ["Total Debt", "TotalDebt"])
    eq  = safe_lookup(bal, ["Stockholders Equity", "StockholdersEquity"])
    ta  = safe_lookup(bal, ["Total Assets", "TotalAssets"])
    
    return {
        "current_ratio":  (ca / cl).round(2).fillna(0),           
        "quick_ratio":    ((ca - inv) / cl).round(2).fillna(0),   
        "debt_to_equity": (td / eq).round(2).fillna(0),           
        "debt_to_assets": (td / ta).round(2).fillna(0),           
    }

def valuation(info, inc, bal, cf):
    """Computes pricing metrics mapped against chronological time series indices."""
    price  = info.get("currentPrice", info.get("previousClose", 0))
    eps    = info.get("trailingEps", 0)
    bvps   = info.get("bookValue", 0)
    mktcap = info.get("marketCap", 0)
    
    # Extract structural scalar elements mapping to the LATEST chronological report year
    ebitda_series = safe_lookup(inc, ["EBITDA"])
    debt_series   = safe_lookup(bal, ["Total Debt", "TotalDebt"])
    cash_series   = safe_lookup(bal, ["Cash And Cash Equivalents", "CashAndCashEquivalents"])
    fcf_series    = safe_lookup(cf, ["Free Cash Flow", "FreeCashFlow"])
    
    # Grab the single first item (most recent report date element)
    ebitda = ebitda_series.iloc[0] if not ebitda_series.empty else 0
    debt   = debt_series.iloc[0] if not debt_series.empty else 0
    cash   = cash_series.iloc[0] if not cash_series.empty else 0
    fcf    = fcf_series.iloc[0] if not fcf_series.empty else 0
    
    ev     = mktcap + debt - cash  
    
    return {
        "pe_ratio":     round(price / eps, 2) if eps else 0,
        "pb_ratio":     round(price / bvps, 2) if bvps else 0,
        "ev_ebitda":    round(ev / ebitda, 2) if ebitda else 0,
        "fcf_yield":    round(fcf / mktcap * 100, 2) if mktcap else 0,
    }