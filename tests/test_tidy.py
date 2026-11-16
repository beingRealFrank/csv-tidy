import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import csv_tidy as t

EX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "messy.csv")


def load():
    return pd.read_csv(EX, dtype=str, keep_default_na=False)


def test_snake():
    assert t.snake(" Full Name ") == "full_name"
    assert t.snake("E-mail") == "e_mail"


def test_phone_and_date():
    assert t.norm_phone("1-555-010-3000") == "(555) 010-3000"
    assert t.norm_phone("12") == "12"
    assert t.parse_date("Mar 9, 2026") == "2026-03-09"
    assert t.parse_date("03/04/2026") == "2026-03-04"
    assert t.parse_date("not a date") == "not a date"


def test_tidy_dedupes_and_counts():
    out, rows_in, ch = t.tidy(load(), key="e-mail")
    assert rows_in == 4 and len(out) == 3
    assert list(out.columns) == ["full_name", "e_mail", "phone_number", "signup_date", "city"]
    assert ch["duplicate rows dropped"] == 1
    assert out.loc[0, "signup_date"] == "2026-03-04"
    assert out.loc[1, "e_mail"] == "sam.sample@example.org"
    assert out.loc[2, "city"] == "Capital City"


def test_missing_key():
    try:
        t.tidy(load(), key="nope")
    except SystemExit:
        return
    raise AssertionError


def test_cli(tmp_path):
    o, r = tmp_path / "o.csv", tmp_path / "r.md"
    t.main([EX, "--key", "e-mail", "--out", str(o), "--report", str(r)])
    assert len(pd.read_csv(o)) == 3
    assert "rows out: 3" in r.read_text()
