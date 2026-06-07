# Financial Statement Analyzer
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bckenz-ai/financial-analyzer/blob/main/notebooks/exploration.ipynb)

> A Python CLI tool for fundamental analysis of publicly traded companies. Pulls financial statements via Yahoo Finance (yfinance), computes 12+ key ratios across profitability, liquidity, solvency, and valuation, and generates three visual reports to assess financial health.

Built as part of a finance and data science portfolio, grounded in hands-on experience with technical and fundamental market analysis.

---

## Features

- Fetches income statement, balance sheet, and cash flow data for any publicly listed ticker
- Computes 12+ financial ratios grouped by category
- Scores each category (0-2) and produces an overall health grade (Strong / Fair / Weak)
- Generates three charts: Revenue vs Net Income Trend, Health Scorecard, and Multi-Period Ratio Trends
- Defensive data layer handles naming inconsistencies and rate-limiting across international tickers

---

## Tech Stack

Python · pandas · yfinance · matplotlib · requests

---

## Project Structure

```
financial-analyzer/
├── src/
│   ├── fetcher.py       # Data retrieval via yfinance with browser session emulation
│   ├── ratios.py        # Profitability, liquidity/solvency, and valuation ratio computation
│   ├── analyzer.py      # Scoring system and health grade assignment
│   └── visualizer.py    # Chart generation for all three visual reports
├── notebooks/
│   └── exploration.ipynb  # Full AAPL analysis with interpretation and references
├── reports/             # Output charts (auto-generated on run)
├── main.py              # CLI entry point
├── .env.example         # Environment variable template
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/bckenz-ai/financial-analyzer.git
cd financial-analyzer

python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

---

## Usage

```bash
python main.py AAPL
python main.py MSFT
python main.py JFC.PS
```

Charts are saved to the `reports/` folder automatically.

---

## Sample Output: Apple Inc. (AAPL)

| Metric | Value |
|---|---|
| Net Margin | 26.92% |
| ROE | 151.91% |
| ROA | 31.18% |
| Current Ratio | 0.89 |
| D/E Ratio | 1.34 |
| P/E Ratio | 38.16 |
| EV/EBITDA | 32.42 |
| FCF Yield | 2.13% |
| **Final Grade** | **Weak (4/10)*** |

*The Weak grade reflects Apple's capital structure strategy (deliberate leverage via buybacks, low current ratio from high cash deployment) and premium valuation, not operational weakness. See `notebooks/exploration.ipynb` for the full qualified interpretation.

---

## Notebook

The `notebooks/exploration.ipynb` file contains a full walkthrough of the tool applied to AAPL, including:

- Ratio definitions and formulas
- Full metric output with interpretation
- Qualification of the scoring model's limitations for premium-quality companies
- APA-formatted references

---

## Ratios Covered

**Profitability:** Gross Margin, Net Margin, EBITDA Margin, ROE, ROA

**Liquidity / Solvency:** Current Ratio, Quick Ratio, Debt-to-Equity, Debt-to-Assets

**Valuation:** P/E Ratio, P/B Ratio, EV/EBITDA, FCF Yield
