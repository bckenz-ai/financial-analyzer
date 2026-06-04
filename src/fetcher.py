import requests
import pandas as pd
import yfinance as yf

def get_financials(ticker: str) -> dict:
    """
    Fetches financial statements from yfinance using browser emulation headers.
    Defensively isolated to protect international data lookups.
    """
    print(f"Establishing secure session wrapper for {ticker}...")
    
    # 1. Build an authentic browser session footprint
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    })
    
    # 2. Attach the session to yfinance
    stock = yf.Ticker(ticker, session=session)
    
    # 3. Pull structural tables independently
    inc_df = stock.financials
    bal_df = stock.balance_sheet
    cf_df  = stock.cashflow
    
    # Hard stop verification layer
    if inc_df is None or inc_df.empty or bal_df is None or bal_df.empty:
        print(f"\nSCRAPER ERROR: Yahoo Finance returned empty statements for {ticker}.")
        print("Yahoo may be temporarily rate-limiting your local IP address.")
        return {"income_stmt": pd.DataFrame(), "balance_sheet": pd.DataFrame(), "cash_flow": pd.DataFrame(), "info": {}}
        
    # 4. Defensive Metadata Lookup (Revised with clean zero fallbacks)
    info_dict = {}
    try:
        raw_info = stock.info
        if raw_info and isinstance(raw_info, dict):
            info_dict = {
                "currentPrice": float(raw_info.get("currentPrice", raw_info.get("previousClose", 0.0))),
                "trailingEps": float(raw_info.get("trailingEps", 0.0)),
                "marketCap": float(raw_info.get("marketCap", 0.0)),
                "bookValue": float(raw_info.get("bookValue", 0.0))
            }
    except Exception:
        # Fallback for international tickers where .info lookups break completely
        print(f"Metadata summary lookup restricted for {ticker}. Pulling live closing price...")
        
        # Pull live close price from history safely as a backup
        price_history = stock.history(period="1d")
        fallback_price = float(price_history["Close"].iloc[0]) if not price_history.empty else 0.0
        
        # FIX: Set missing metrics to 0.0 instead of hardcoding arbitrary estimates
        info_dict = {
            "currentPrice": fallback_price,
            "trailingEps": 0.0,  
            "marketCap": 0.0,
            "bookValue": 0.0
        }

    return {
        "income_stmt":  inc_df,
        "balance_sheet": bal_df,
        "cash_flow":    cf_df,
        "info":         info_dict
    }