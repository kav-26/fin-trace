"""
Fin-Trace: Financial Analyst Agent
Computes derived financial metrics (YoY change, margins) from structured
data using Pandas — actual math, not LLM-recited numbers.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FINANCIAL_DATA_DIR = PROJECT_ROOT / "data" / "financial"

CURRENT_COMPANY = "tsla"  # <-- change this to switch companies: "msft" or "tsla"

def load_financial_data() -> pd.DataFrame:
    """Load the structured financial data CSV for the current company."""
    path = FINANCIAL_DATA_DIR / f"{CURRENT_COMPANY}_financials.csv"
    return pd.read_csv(path)


def compute_yoy_changes(df: pd.DataFrame) -> pd.DataFrame:
    """Add year-over-year absolute and percentage change columns."""
    df = df.copy()
    df["yoy_change"] = df["fy2023"] - df["fy2022"]
    df["yoy_pct_change"] = ((df["fy2023"] - df["fy2022"]) / df["fy2022"] * 100).round(2)
    return df


def compute_margins(df: pd.DataFrame) -> dict:
    """Compute gross and operating margin percentages for each year, where possible."""
    def get_value(metric, segment="Total"):
        row = df[(df["metric"] == metric) & (df["segment"] == segment)]
        return row.iloc[0] if not row.empty else None

    revenue = get_value("revenue")
    gross_margin = get_value("gross_margin")
    operating_income = get_value("operating_income")

    margins = {}
    if revenue is not None and gross_margin is not None:
        margins["gross_margin_pct_fy2022"] = round(gross_margin["fy2022"] / revenue["fy2022"] * 100, 2)
        margins["gross_margin_pct_fy2023"] = round(gross_margin["fy2023"] / revenue["fy2023"] * 100, 2)

    if revenue is not None and operating_income is not None:
        margins["operating_margin_pct_fy2022"] = round(operating_income["fy2022"] / revenue["fy2022"] * 100, 2)
        margins["operating_margin_pct_fy2023"] = round(operating_income["fy2023"] / revenue["fy2023"] * 100, 2)

    return margins


def analyze() -> dict:
    """Run the full financial analysis: YoY changes + margins."""
    df = load_financial_data()
    df_with_changes = compute_yoy_changes(df)
    margins = compute_margins(df)

    return {
        "yoy_table": df_with_changes.to_dict(orient="records"),
        "margins": margins
    }


def format_for_llm(analysis: dict) -> str:
    """Format the analysis as readable text for the Reviewer agent to use as grounded evidence."""
    lines = ["VERIFIED FINANCIAL METRICS (computed, not LLM-estimated):\n"]

    for row in analysis["yoy_table"]:
        lines.append(
            f"- {row['metric']} ({row['segment']}): "
            f"FY2022=${row['fy2022']:,}M → FY2023=${row['fy2023']:,}M "
            f"(Δ ${row['yoy_change']:,}M, {row['yoy_pct_change']}%)"
        )

    lines.append("\nMargins:")
    for key, val in analysis["margins"].items():
        lines.append(f"- {key.replace('_', ' ')}: {val}%")

    return "\n".join(lines)


if __name__ == "__main__":
    analysis = analyze()

    print("\n📊 Financial Analysis (computed via Pandas)\n")
    print(format_for_llm(analysis))