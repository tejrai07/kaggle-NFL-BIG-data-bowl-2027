"""Stage A data audit. Chunked, Kaggle-compatible. Writes reports/schema_tables.md and schema_report.json.
Usage: python scripts/inspect_data.py [data_dir]"""
import sys, json, os, glob
import pandas as pd
CANDIDATES = ["/kaggle/input/nfl-big-data-bowl-2027", "data/raw", "."]
def find_dir(arg):
    for d in ([arg] if arg else CANDIDATES):
        if d and glob.glob(os.path.join(d, "**/*.csv"), recursive=True): return d
    sys.exit("No CSV files found; pass the data directory explicitly.")
def profile(path, chunksize=500_000):
    rows, nulls, dtypes, first, nun = 0, None, None, None, {}
    for ch in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        if first is None:
            first, dtypes, nulls = ch.head(3), ch.dtypes.astype(str).to_dict(), ch.isna().sum()
        else:
            nulls = nulls.add(ch.isna().sum(), fill_value=0)
        rows += len(ch)
        for c in ch.columns:
            if c.lower().endswith("id") or c in ("season", "position", "drill"):
                nun.setdefault(c, set()).update(ch[c].dropna().unique().tolist())
    return {"rows": rows, "dtypes": dtypes, "null_counts": nulls.astype(int).to_dict(),
            "n_unique_id_like": {k: len(v) for k, v in nun.items()}, "sample": first.to_dict("records")}
if __name__ == "__main__":
    d = find_dir(sys.argv[1] if len(sys.argv) > 1 else None)
    files = sorted(glob.glob(os.path.join(d, "**/*.csv"), recursive=True))
    report = {os.path.relpath(f, d): profile(f) for f in files}
    os.makedirs("reports", exist_ok=True)
    json.dump(report, open("reports/schema_report.json", "w"), indent=2, default=str)
    with open("reports/schema_tables.md", "w") as o:
        o.write("# Data inventory (auto-generated)\n\n")
        for f, r in report.items():
            o.write(f"## {f}\nrows: {r['rows']:,}\n\n| column | dtype | nulls |\n|---|---|---|\n")
            o.writelines(f"| {c} | {t} | {r['null_counts'][c]} |\n" for c, t in r["dtypes"].items())
            o.write("\n")
    print(f"Profiled {len(files)} files from {d}")
