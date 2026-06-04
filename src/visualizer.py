import matplotlib.pyplot as plt
import pandas as pd

def plot_revenue_trend(income_stmt, ticker):
    """
    Generates a clean bar vs line trend chart with automatic date string scaling.
    Renders inline cleanly inside Jupyter notebooks.
    """
    clean_stmt = income_stmt.copy()
    clean_stmt.columns = pd.to_datetime(clean_stmt.columns).strftime('%Y-%m-%d')
    
    normalized_rows = clean_stmt.index.astype(str).str.lower().str.replace(" ", "")
    rev_idx = normalized_rows.get_loc("totalrevenue") if "totalrevenue" in normalized_rows.values else 0
    ni_idx = normalized_rows.get_loc("netincome") if "netincome" in normalized_rows.values else 0
    
    rev = clean_stmt.iloc[rev_idx].sort_index()
    ni  = clean_stmt.iloc[ni_idx].sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    x_labels = rev.index.astype(str)
    
    ax.bar(x_labels, rev / 1e9, label="Revenue (B)", alpha=0.7, color="#378ADD", width=0.4)
    ax.plot(x_labels, ni / 1e9, label="Net Income (B)", color="#1D9E75", marker="o", linewidth=2)
    
    ax.set_title(f"{ticker} — Revenue vs Net Income Trend", fontsize=12, fontweight='bold', pad=15)
    ax.set_ylabel("USD Billions", fontsize=10, fontweight='bold')
    ax.set_xlabel("Fiscal Year End", fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.legend(loc="upper left")
    
    plt.tight_layout()
    plt.savefig(f"reports/{ticker}_revenue_trend.png", dpi=150)
    
    # FIX: Add plt.show() so it displays in your notebook instead of closing silently
    plt.show()
    plt.close(fig) 

def plot_scorecard(score_breakdown: dict, ticker: str):
    """
    Generates a structured fundamental checklist bar plot with distinct row baselines.
    Defensively filters out text grade metadata strings to prevent plotting crashes.
    """
    # 1. Isolate ONLY the real numerical category metrics for the chart plotting variables
    numeric_scores = {k: v for k, v in score_breakdown.items() if not k.startswith("_")}
    
    labels = list(numeric_scores.keys())
    values = list(numeric_scores.values())
    
    colors = ["#1D9E75" if v == 2 else "#EF9F27" if v == 1 else "#E24B4A" for v in values]
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    # Draw horizontal bars safely using numerical values
    bars = ax.barh(labels, values, color=colors, height=0.5, zorder=2)
    
    # FIX: Removed the '*' unpacking operator to pass width limits without a height conflict
    ax.barh(labels, [2] * len(labels), color='gray', alpha=0.08, height=0.5, zorder=0)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.05, 
            bar.get_y() + bar.get_height()/2, 
            f" Score: {int(width)}/2", 
            va='center', ha='left', fontsize=9, fontweight='bold', color="#333333"
        )
        
    # Extract calculated score summaries for the chart title text
    total = score_breakdown.get("_total_score", sum(values))
    grade = score_breakdown.get("_final_grade", "N/A")
    
    ax.set_xlim(0, 2.3) 
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["0 (Weak)", "1 (Average)", "2 (Strong)"], fontsize=9)
    
    ax.set_title(f"{ticker} — Health Scorecard  [Total: {total}/10 | Grade: {grade}]", 
                 fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='x', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f"reports/{ticker}_scorecard.png", dpi=150)
    
    # Render inline inside notebook displays
    plt.show()
    plt.close(fig)

def plot_ratio_trends(prof_df, liq_df, ticker):
    """
    Generates a multi-period line chart tracking key financial ratios over time.
    Defensively aligns data arrays to ensure matching dimensional shapes.
    """
    # 1. Standardize formatting shapes: Transpose if metrics are stored as columns
    prof_clean = prof_df.T
    liq_clean = liq_df.T
    
    # 2. Normalize date index formats to simple Year strings ('YYYY')
    prof_clean.columns = pd.to_datetime(prof_clean.columns).strftime('%Y')
    liq_clean.columns = pd.to_datetime(liq_clean.columns).strftime('%Y')
    
    # 3. CRITICAL ALIGNMENT FIX: Identify only the overlapping years in both sheets
    # This filters out the extra 5th year from the balance sheet automatically
    common_years = prof_clean.columns.intersection(liq_clean.columns)
    
    # Sort chronologically from oldest year to newest year
    years_sorted = sorted(list(common_years))
    
    # 4. Slice out metrics matching the shared timeline cleanly
    net_margin = prof_clean.loc["net_margin", years_sorted].values
    roe        = prof_clean.loc["roe", years_sorted].values
    curr_ratio = liq_clean.loc["current_ratio", years_sorted].values

    # 5. Initialize the dual-axis chart setup
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Left Axis: Profitability percentages
    color1 = "#1D9E75"
    color2 = "#378ADD"
    line1 = ax1.plot(years_sorted, net_margin, marker='o', linewidth=2.5, color=color1, label="Net Margin (%)")
    line2 = ax1.plot(years_sorted, roe, marker='s', linewidth=2.5, color=color2, label="Return on Equity (%)")
    ax1.set_ylabel("Percentage (%)", fontsize=10, fontweight='bold')
    ax1.tick_params(axis='y')
    
    # Right Axis: Liquidity multipliers
    ax2 = ax1.twinx()
    color3 = "#EF9F27"
    line3 = ax2.plot(years_sorted, curr_ratio, marker='^', linewidth=2, linestyle='--', color=color3, label="Current Ratio (x)")
    ax2.set_ylabel("Ratio Multiplier (x)", fontsize=10, color="#333333", fontweight='bold')
    ax2.tick_params(axis='y')
    
    # 6. Combine all lines into a single, clean legend box
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left", frameon=True, facecolor="white", edgecolor="none")
    
    ax1.set_title(f"{ticker} — Core Financial Ratio Trends (Multi-Period)", fontsize=12, fontweight='bold', pad=15)
    ax1.set_xlabel("Fiscal Reporting Year", fontsize=10)
    ax1.grid(axis='both', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f"reports/{ticker}_ratio_trends.png", dpi=150)
    
    # Render inline safely in your code environment
    plt.show()
    plt.close(fig)