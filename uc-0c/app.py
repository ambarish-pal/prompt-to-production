"""
UC-0C app.py

Calculates month-over-month growth in actual_spend for each ward/category
combination found in the input CSV.

Usage:
    python app.py --input <path_to_csv> --output <path_to_write_csv>
"""
import argparse
import csv
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate month-over-month growth in actual_spend per ward/category."
    )
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--output", required=True, help="Path to write the output CSV file.")
    return parser.parse_args()


def read_rows(input_path):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def to_float_or_none(value):
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def main():
    args = parse_args()

    rows = read_rows(args.input)

    # Group rows by (ward, category) so growth is calculated within each series
    # over time (month-over-month), not across unrelated wards/categories.
    groups = defaultdict(list)
    for row in rows:
        ward = row.get("ward", "")
        category = row.get("category", "")
        period = row.get("period", "")
        actual_spend = to_float_or_none(row.get("actual_spend"))
        groups[(ward, category)].append({
            "period": period,
            "actual_spend": actual_spend,
        })

    output_rows = []

    for (ward, category), entries in groups.items():
        # Sort chronologically by period (YYYY-MM sorts correctly as a string).
        entries.sort(key=lambda e: e["period"])

        previous_spend = None
        previous_period = None

        for entry in entries:
            period = entry["period"]
            actual_spend = entry["actual_spend"]

            growth_amount = ""
            growth_pct = ""

            if actual_spend is not None and previous_spend is not None:
                growth_amount = round(actual_spend - previous_spend, 4)
                if previous_spend != 0:
                    growth_pct = round((actual_spend - previous_spend) / previous_spend * 100, 2)
                else:
                    growth_pct = ""

            output_rows.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": actual_spend if actual_spend is not None else "",
                "previous_period": previous_period if previous_period else "",
                "previous_actual_spend": previous_spend if previous_spend is not None else "",
                "growth_amount": growth_amount,
                "growth_pct": growth_pct,
            })

            # Only update the "previous" pointers when we have a real value,
            # so a single missing month doesn't silently reset the series.
            if actual_spend is not None:
                previous_spend = actual_spend
                previous_period = period

    # Keep a stable, readable ordering in the output file.
    output_rows.sort(key=lambda r: (r["ward"], r["category"], r["period"]))

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "previous_period",
        "previous_actual_spend",
        "growth_amount",
        "growth_pct",
    ]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote growth data for {len(output_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
