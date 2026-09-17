"""
load_to_db.py
--------------
Loads the relational e-commerce dataset from an Excel workbook, applies
light cleaning/validation, and writes it into a SQLite database with
a proper relational schema (primary keys, foreign keys, correct dtypes).

Usage:
    python load_to_db.py
    python load_to_db.py --source ../data/ecommerce_relational.xlsx --db ../db/ecommerce.db
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip currency/unit suffixes like ' (€)' from column names so SQL
    columns are easy to reference (e.g. 'TotalAmount (€)' -> 'TotalAmount')."""
    df = df.copy()
    df.columns = [c.split(" (")[0].strip() for c in df.columns]
    return df


def load_sheets(source: Path) -> dict[str, pd.DataFrame]:
    xls = pd.ExcelFile(source)
    sheets = {}
    for name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=name)
        df = clean_column_names(df)
        sheets[name] = df
    return sheets


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["OrderDate"] = pd.to_datetime(df["OrderDate"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Status"] = df["Status"].str.strip()
    return df


def clean_order_details(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # ReturnReason is legitimately empty for non-returned lines; keep as NULL, not ''
    df["ReturnReason"] = df["ReturnReason"].where(df["ReturnReason"].notna(), None)
    return df


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    return df


def build_schema(conn: sqlite3.Connection) -> None:
    schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def main():
    parser = argparse.ArgumentParser(description="Load e-commerce Excel data into SQLite.")
    parser.add_argument(
        "--source",
        default=str(Path(__file__).parent.parent / "data" / "ecommerce_relational.xlsx"),
        help="Path to the source .xlsx file",
    )
    parser.add_argument(
        "--db",
        default=str(Path(__file__).parent.parent / "db" / "ecommerce.db"),
        help="Path to the output SQLite database",
    )
    args = parser.parse_args()

    source = Path(args.source)
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading source workbook: {source}")
    sheets = load_sheets(source)

    sheets["Orders"] = clean_orders(sheets["Orders"])
    sheets["Order Details"] = clean_order_details(sheets["Order Details"])
    sheets["Date"] = clean_dates(sheets["Date"])

    # Fresh database each run, so this script is safely re-runnable
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    print("Creating schema...")
    build_schema(conn)

    table_map = {
        "Categories": "categories",
        "Customers": "customers",
        "Products": "products",
        "Date": "date_dim",
        "Orders": "orders",
        "Order Details": "order_details",
    }

    for sheet_name, table_name in table_map.items():
        df = sheets[sheet_name]
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"  Loaded {len(df):>4} rows -> {table_name}")

    # Sanity check: foreign keys are consistent
    conn.execute("PRAGMA foreign_key_check")
    issues = conn.execute("PRAGMA foreign_key_check").fetchall()
    if issues:
        print("WARNING: foreign key issues found:", issues)
    else:
        print("Foreign key check passed.")

    conn.commit()
    conn.close()
    print(f"\nDone. Database written to: {db_path}")


if __name__ == "__main__":
    main()
