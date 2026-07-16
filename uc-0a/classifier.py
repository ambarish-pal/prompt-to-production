"""
classifier.py

Naive first-pass classifier for citizen complaints.
Reads a CSV of complaints and writes out a new CSV with two extra
columns: `category` and `priority`, derived from simple keyword
matching against the complaint `description` (and `days_open` for
priority escalation).

Usage:
    python classifier.py --input <path_to_input_csv> --output <path_to_output_csv>
"""

import argparse
import csv


# Keyword -> category mapping. Order matters: first match wins.
CATEGORY_KEYWORDS = [
    ("Roads & Potholes", [
        "pothole", "road surface", "cracked", "sinking", "manhole",
        "footpath", "pavement",
    ]),
    ("Water Logging & Drainage", [
        "flood", "flooded", "drain", "waterlog", "stranded", "rain",
    ]),
    ("Street Lighting", [
        "streetlight", "street light", "lights out", "flickering",
        "sparking", "dark at night", "lighting",
    ]),
    ("Sanitation & Garbage", [
        "garbage", "waste", "dead animal", "smell", "trash",
        "dumped", "overflowing",
    ]),
    ("Noise Complaint", [
        "music", "noise", "loud", "wedding venue",
    ]),
    ("Public Safety", [
        "injury", "hazard", "risk", "safety", "electrical",
        "accident", "fell",
    ]),
]

DEFAULT_CATEGORY = "Other"

# Keywords that indicate an urgent / high priority complaint.
HIGH_PRIORITY_KEYWORDS = [
    "injury", "injured", "hazard", "risk", "electrical", "sparking",
    "health", "children", "school", "stranded", "flooded", "fell",
    "serious",
]

MEDIUM_PRIORITY_KEYWORDS = [
    "safety", "concern", "elderly", "affected", "blocked",
]


def classify_category(description):
    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in text:
                return category
    return DEFAULT_CATEGORY


def classify_priority(description, days_open):
    text = description.lower()

    # Keyword-based urgency signal.
    keyword_priority = "Low"
    if any(kw in text for kw in HIGH_PRIORITY_KEYWORDS):
        keyword_priority = "High"
    elif any(kw in text for kw in MEDIUM_PRIORITY_KEYWORDS):
        keyword_priority = "Medium"

    # Escalate based on how long the complaint has been open.
    try:
        days = int(days_open)
    except (TypeError, ValueError):
        days = 0

    if days >= 15:
        days_priority = "High"
    elif days >= 7:
        days_priority = "Medium"
    else:
        days_priority = "Low"

    # Take the higher of the two signals.
    order = {"Low": 0, "Medium": 1, "High": 2}
    final_priority = max(keyword_priority, days_priority, key=lambda p: order[p])
    return final_priority


def main():
    parser = argparse.ArgumentParser(
        description="Classify citizen complaints by category and priority."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["category", "priority"]
        rows = []
        for row in reader:
            description = row.get("description", "") or ""
            days_open = row.get("days_open", "")
            row["category"] = classify_category(description)
            row["priority"] = classify_priority(description, days_open)
            rows.append(row)

    with open(args.output, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Classified {len(rows)} complaints -> {args.output}")


if __name__ == "__main__":
    main()
