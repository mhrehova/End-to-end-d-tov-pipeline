"""
analysis.py
-----------
Runs the SQL queries in sql/queries/ against the SQLite database and
produces a small set of charts summarizing the key findings:

    1. Margin (EUR and %) by product category
    2. Top 10 customers by revenue
    3. Return rate by category
    4. Margin decay by discount band

Usage:
    python analysis.py
    python analysis.py --db ../db/ecommerce.db --out ../output
"""

import argparse
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no display needed, just save files
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.size"] = 10


def run_query(conn: sqlite3.Connection, sql_path: Path) -> pd.DataFrame:
    with open(sql_path, "r", encoding="utf-8") as f:
        query = f.read()
    return pd.read_sql_query(query, conn)


def chart_margin_by_category(df: pd.DataFrame, out_dir: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(8, 5))

    x = range(len(df))
    ax1.bar(x, df["MarginEUR"], color="#2E7D32", label="Marža (€)")
    ax1.set_ylabel("Marža (€)", color="#2E7D32")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["CategoryName"], rotation=30, ha="right")
    ax1.tick_params(axis="y", labelcolor="#2E7D32")

    ax2 = ax1.twinx()
    ax2.plot(x, df["MarginPct"], color="#D32F2F", marker="o", label="Marža (%)")
    ax2.set_ylabel("Marža (%)", color="#D32F2F")
    ax2.tick_params(axis="y", labelcolor="#D32F2F")

    plt.title("Marža podľa kategórie: € vs. %")
    fig.tight_layout()
    fig.savefig(out_dir / "margin_by_category.png")
    plt.close(fig)


def chart_top_customers(df: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    df_sorted = df.sort_values("TotalRevenue")
    ax.barh(df_sorted["CustomerName"], df_sorted["TotalRevenue"], color="#1565C0")
    ax.set_xlabel("Celkové tržby (€)")
    ax.set_title("Top 10 zákazníkov podľa tržieb")
    fig.tight_layout()
    fig.savefig(out_dir / "top_customers.png")
    plt.close(fig)


def chart_return_rate(df: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    df_sorted = df.sort_values("ReturnRatePct")
    colors = ["#C62828" if v > 0 else "#9E9E9E" for v in df_sorted["ReturnRatePct"]]
    ax.barh(df_sorted["CategoryName"], df_sorted["ReturnRatePct"], color=colors)
    ax.set_xlabel("Return rate (%)")
    ax.set_title("Return rate podľa kategórie")
    fig.tight_layout()
    fig.savefig(out_dir / "return_rate.png")
    plt.close(fig)


def chart_discount_impact(df: pd.DataFrame, out_dir: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(8, 5))

    x = range(len(df))
    ax1.bar(x, df["UnitsSold"], color="#8D6E63", alpha=0.7, label="Predané kusy")
    ax1.set_ylabel("Predané kusy", color="#8D6E63")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["DiscountBand"])
    ax1.tick_params(axis="y", labelcolor="#8D6E63")

    ax2 = ax1.twinx()
    ax2.plot(x, df["AvgMarginPct"], color="#EF6C00", marker="o", linewidth=2, label="Priem. marža (%)")
    ax2.set_ylabel("Priemerná marža (%)", color="#EF6C00")
    ax2.tick_params(axis="y", labelcolor="#EF6C00")

    plt.title("Dopad hĺbky zľavy na maržu a objem")
    fig.tight_layout()
    fig.savefig(out_dir / "discount_impact_on_margin.png")
    plt.close(fig)


def print_key_findings(margin_df, customers_df, returns_df, discount_df) -> None:
    print("\n=== Kľúčové zistenia ===\n")

    worst_margin_pct = margin_df.loc[margin_df["MarginPct"].idxmin()]
    print(
        f"- '{worst_margin_pct['CategoryName']}' má najvyšší objem tržieb "
        f"({worst_margin_pct['Revenue']:.0f} €), ale najnižšiu percentuálnu maržu "
        f"({worst_margin_pct['MarginPct']:.1f} %)."
    )

    top_cust = customers_df.iloc[0]
    most_orders_cust = customers_df.loc[customers_df["OrderCount"].idxmax()]
    print(
        f"- Najvyššie tržby má '{top_cust['CustomerName']}' ({top_cust['TotalRevenue']:.0f} €), "
        f"no najviac objednávok má '{most_orders_cust['CustomerName']}' "
        f"({most_orders_cust['OrderCount']} objednávok, priemerná hodnota len "
        f"{most_orders_cust['AvgOrderValue']:.0f} €)."
    )

    top_return = returns_df.iloc[0]
    print(
        f"- Najvyšší return rate má kategória '{top_return['CategoryName']}' "
        f"({top_return['ReturnRatePct']:.1f} %) — pozor, vzorka vrátení je malá, "
        f"takže toto číslo treba brať orientačne."
    )

    no_discount = discount_df[discount_df["DiscountBand"] == "0% (bez zľavy)"].iloc[0]
    highest_discount = discount_df.iloc[-1]
    drop = no_discount["AvgMarginPct"] - highest_discount["AvgMarginPct"]
    print(
        f"- Marža klesá takmer lineárne so zľavou: z {no_discount['AvgMarginPct']:.1f} % "
        f"(bez zľavy) na {highest_discount['AvgMarginPct']:.1f} % (zľava {highest_discount['DiscountBand']}), "
        f"pokles o {drop:.1f} percentuálneho bodu."
    )


def main():
    parser = argparse.ArgumentParser(description="Run analysis queries and generate charts.")
    parser.add_argument("--db", default=str(Path(__file__).parent.parent / "db" / "ecommerce.db"))
    parser.add_argument("--out", default=str(Path(__file__).parent.parent / "output"))
    args = parser.parse_args()

    db_path = Path(args.db)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    queries_dir = Path(__file__).parent.parent / "sql" / "queries"

    conn = sqlite3.connect(db_path)

    margin_df = run_query(conn, queries_dir / "margin_by_category.sql")
    customers_df = run_query(conn, queries_dir / "top_customers.sql")
    returns_df = run_query(conn, queries_dir / "return_rate.sql")
    discount_df = run_query(conn, queries_dir / "discount_impact_on_margin.sql")

    conn.close()

    chart_margin_by_category(margin_df, out_dir)
    chart_top_customers(customers_df, out_dir)
    chart_return_rate(returns_df, out_dir)
    chart_discount_impact(discount_df, out_dir)

    print(f"Charts saved to: {out_dir}")
    print_key_findings(margin_df, customers_df, returns_df, discount_df)


if __name__ == "__main__":
    main()
