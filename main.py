from src.fetcher import get_financials
from src.ratios import profitability, liquidity_solvency, valuation
from src.analyzer import overall_score
from src.visualizer import plot_revenue_trend, plot_scorecard, plot_ratio_trends

import sys
import os
import json
import pandas as pd

def analyze(ticker: str):
    print(f"\nFetching financial statements for {ticker}...")
    data = get_financials(ticker)
    
    inc = data.get("income_stmt")
    bal = data.get("balance_sheet")
    cf  = data.get("cash_flow")
    info = data.get("info", {})
    
    if inc is None or inc.empty or bal.empty or cf.empty:
        print(f"Error: Missing financial statement records for {ticker}.")
        return

    # 1. Compute historical ratios (These are dicts of multi-year Pandas Series)
    prof_hist = profitability(inc, bal)
    liq_hist = liquidity_solvency(bal)
    
    # 2. BULLETPROOF EXTRACTION: Pull index 0 from each Series to keep the dictionary keys
    latest_ratios = {}
    
    for metric_name, series in prof_hist.items():
        # Grabs the most recent year's value while keeping the metric name as the key
        latest_ratios[metric_name] = series.iloc[0] if not series.empty else 0.0
        
    for metric_name, series in liq_hist.items():
        latest_ratios[metric_name] = series.iloc[0] if not series.empty else 0.0

    # 3. Add valuation metrics (already a flat single-year dictionary)
    latest_val = valuation(info, inc, bal, cf)
    latest_ratios.update(latest_val)
    
    # Debug print statement: See exactly what keys are passing
    print("\n--- Extracted Latest Metrics Passed to Analyzer ---")
    for k, v in latest_ratios.items():
        print(f"  {k}: {v}")
    
    # 4. Calculate Scores
    print("\nEvaluating financial health score...")
    score_breakdown = overall_score(latest_ratios)
    
    print("\n=== FINAL ANALYSIS SCORES ===")
    print(score_breakdown)
    
    # 5. Plotting (Pass raw unmodified statements so the graphs remain multi-year)
    print("\n=== GENERATING VISUALIZATIONS ===")
    os.makedirs("reports", exist_ok=True)
    
    print(f"Generating Revenue vs Net Income chart...")
    plot_revenue_trend(inc, ticker)
    
    print(f"Generating Health Scorecard chart...")
    plot_scorecard(score_breakdown, ticker)
    
    # NEW: Convert historical ratio dictionaries into full multi-year DataFrames
    # and pass them directly to generate the multi-period line graph trend report.
    print(f"Generating Multi-Period Ratio Trends chart...")
    prof_df = pd.DataFrame(prof_hist)
    liq_df = pd.DataFrame(liq_hist)
    plot_ratio_trends(prof_df, liq_df, ticker)
    
    print(f"\nCharts saved inside the 'reports/' folder.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker_symbol = sys.argv[1].upper()
        analyze(ticker_symbol)
    else:
        print("Please provide a ticker symbol. Example: python main.py AAPL")