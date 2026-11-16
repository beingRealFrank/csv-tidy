"""csv-tidy: clean a messy CSV/XLSX and write out.csv + report.md."""
import argparse
import re
import sys
from collections import Counter
from datetime import datetime

import pandas as pd

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d %b %Y", "%b %d, %Y", "%B %d, %Y", "%Y/%m/%d"]


def snake(name: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z]+", "_", str(name).strip()).strip("_").lower()
    return s or "column"


def parse_date(v):
    v = str(v).strip()
    for f in DATE_FORMATS:
        try:
            return datetime.strptime(v, f).date().isoformat()
        except ValueError:
            pass
    return v


def norm_email(v):
    v = str(v).strip().lower()
    return v if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v) else v


def norm_phone(v):
    digits = re.sub(r"\D", "", str(v))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return str(v).strip()


def tidy(df: pd.DataFrame, key: str | None = None):
    changes = Counter()
    rows_in = len(df)
    df = df.copy()
    new_cols = [snake(c) for c in df.columns]
    changes["headers renamed"] = sum(a != b for a, b in zip(df.columns, new_cols))
    df.columns = new_cols
    df = df.astype(object).where(df.notna(), "")
    for c in df.columns:
        before = df[c].astype(str)
        stripped = before.str.strip().str.replace(r"\s+", " ", regex=True)
        changes["cells trimmed"] += int((before != stripped).sum())
        df[c] = stripped
    for c in df.columns:
        if "mail" in c:
            new = df[c].map(norm_email); changes["emails normalised"] += int((new != df[c]).sum()); df[c] = new
        elif "phone" in c:
            new = df[c].map(lambda v: norm_phone(v) if v else v); changes["phones normalised"] += int((new != df[c]).sum()); df[c] = new
        elif "date" in c:
            new = df[c].map(lambda v: parse_date(v) if v else v); changes["dates to ISO"] += int((new != df[c]).sum()); df[c] = new
    if key:
        key = snake(key)
        if key not in df.columns:
            raise SystemExit(f"key column not found: {key}")
        keyed = df[key].astype(str).str.lower()
        dup = keyed.duplicated() & (keyed != "")
        changes["duplicate rows dropped"] = int(dup.sum())
        df = df[~dup]
    return df.reset_index(drop=True), rows_in, changes


def report(rows_in, rows_out, changes) -> str:
    lines = ["# csv-tidy report", "", f"- rows in: {rows_in}", f"- rows out: {rows_out}", "", "## Changes"]
    for k in ["headers renamed", "cells trimmed", "emails normalised", "phones normalised", "dates to ISO", "duplicate rows dropped"]:
        lines.append(f"- {k}: {changes.get(k, 0)}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Clean a messy CSV/XLSX file.")
    ap.add_argument("input")
    ap.add_argument("--key", help="column to dedupe on (case-insensitive)")
    ap.add_argument("--out", default="out.csv")
    ap.add_argument("--report", default="report.md")
    a = ap.parse_args(argv)
    df = pd.read_excel(a.input, dtype=str) if a.input.lower().endswith((".xlsx", ".xls")) else pd.read_csv(a.input, dtype=str, keep_default_na=False)
    out, rows_in, changes = tidy(df, a.key)
    out.to_csv(a.out, index=False)
    open(a.report, "w").write(report(rows_in, len(out), changes))
    print(f"{rows_in} rows in, {len(out)} rows out -> {a.out}, {a.report}")


if __name__ == "__main__":
    main()
