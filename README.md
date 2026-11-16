# csv-tidy

Cleans a messy CSV or XLSX file and tells you exactly what it changed.

- trims whitespace, normalises headers to `snake_case`
- lowercases emails, formats US phone numbers as `(555) 010-2000`
- converts common date formats to ISO `YYYY-MM-DD`
- optionally drops duplicate rows on a key column (`--key`)
- writes `out.csv` and `report.md` (rows in/out and a count of every kind of change)

```
uv run --with pandas --with openpyxl python csv_tidy.py examples/messy.csv --key e-mail
```

`examples/messy.csv` is synthetic; `examples/clean.csv` and `examples/report.md` show the result.

## Test
```
uv run --with pandas --with openpyxl --with pytest pytest -q
```

MIT licensed.
