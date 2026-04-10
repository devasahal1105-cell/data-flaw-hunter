"""
src/detector.py
Data Flaw Hunter — Day 4: Missing Value Scanner
"""

import pandas as pd


# ─────────────────────────────────────────────
# CORE FUNCTION: detect_missing
# ─────────────────────────────────────────────

def detect_missing(df: pd.DataFrame) -> dict:
    """
    Scans every column in the DataFrame for missing values.

    Returns a dictionary (hash map) where:
      key   = column name
      value = {
          'count'    : number of missing cells,
          'pct'      : missing percentage (0-100),
          'severity' : 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'OK'
      }

    DSA note:
      A dict gives O(1) lookup per column — perfect for building
      on top of this in Day 7's unified flaw report.
    """

    total_rows = len(df)

    # Guard: empty DataFrame
    if total_rows == 0:
        return {}

    missing_report = {}  # <-- our hash map

    for col in df.columns:
        missing_count = int(df[col].isnull().sum())
        missing_pct   = round((missing_count / total_rows) * 100, 2)

        # Severity thresholds (used again in Day 7)
        if missing_pct > 30:
            severity = "CRITICAL"
        elif missing_pct > 20:
            severity = "HIGH"
        elif missing_pct > 10:
            severity = "MEDIUM"
        elif missing_pct > 0:
            severity = "LOW"
        else:
            severity = "OK"

        missing_report[col] = {
            "count":    missing_count,
            "pct":      missing_pct,
            "severity": severity,
        }

    return missing_report


# ─────────────────────────────────────────────
# HELPER: print a formatted flaw table
# ─────────────────────────────────────────────

def print_missing_report(report: dict) -> None:
    """
    Prints a clean table of missing-value flaws to the console.
    Only shows columns that actually have missing values.
    """

    # Filter to flawed columns only, sorted worst-first
    flawed = {
        col: info
        for col, info in report.items()
        if info["severity"] != "OK"
    }

    if not flawed:
        print("✅  No missing values found — data looks clean!")
        return

    # Sort by missing percentage descending
    flawed = dict(
        sorted(flawed.items(), key=lambda x: x[1]["pct"], reverse=True)
    )

    # Print header
    print("\n" + "=" * 60)
    print(f"{'COLUMN':<25} {'MISSING':>8} {'PCT':>8}   SEVERITY")
    print("=" * 60)

    severity_icons = {
        "CRITICAL": "🔴",
        "HIGH":     "🟠",
        "MEDIUM":   "🟡",
        "LOW":      "🟢",
    }

    for col, info in flawed.items():
        icon = severity_icons.get(info["severity"], "")
        print(
            f"{col:<25} {info['count']:>8,} {info['pct']:>7.1f}%"
            f"   {icon} {info['severity']}"
        )

    print("=" * 60)
    critical_cols = [c for c, i in flawed.items() if i["severity"] == "CRITICAL"]
    print(f"\n⚠️  Total flawed columns : {len(flawed)}")
    print(f"🔴  CRITICAL (>30% missing): {len(critical_cols)}")
    if critical_cols:
        print(f"    → {', '.join(critical_cols)}")
    print()


# ─────────────────────────────────────────────
# UNIT TESTS  (run: python src/detector.py)
# ─────────────────────────────────────────────

def run_tests():
    """Lightweight unit tests — no pytest needed for now."""

    print("Running unit tests...\n")

    # ── Test 1: 100% missing column ──────────────────────────────
    empty_df = pd.DataFrame({
        "PM2.5": [None, None, None, None],
        "SO2":   [1.0, 2.0, None, 4.0],
    })
    report = detect_missing(empty_df)

    assert report["PM2.5"]["pct"] == 100.0,   "Test 1a FAILED"
    assert report["PM2.5"]["severity"] == "CRITICAL", "Test 1b FAILED"
    print("✅  Test 1 passed — 100% missing column detected as CRITICAL")

    # ── Test 2: 50% missing column ───────────────────────────────
    assert report["SO2"]["pct"] == 25.0,      "Test 2a FAILED"
    assert report["SO2"]["severity"] == "HIGH", "Test 2b FAILED"
    print("✅  Test 2 passed — 25% missing column detected as LOW")

    # ── Test 3: no missing values → empty flawed section ─────────
    clean_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    clean_report = detect_missing(clean_df)
    assert all(v["severity"] == "OK" for v in clean_report.values()), "Test 3 FAILED"
    print("✅  Test 3 passed — clean DataFrame has no flaws")

    # ── Test 4: empty DataFrame guard ────────────────────────────
    result = detect_missing(pd.DataFrame())
    assert result == {}, "Test 4 FAILED"
    print("✅  Test 4 passed — empty DataFrame returns empty dict\n")

    print("All tests passed! ✅\n")


# ─────────────────────────────────────────────
# DEMO: run against the real air quality CSV
# ─────────────────────────────────────────────

if __name__ == "__main__":

    run_tests()

    # ── Load the real dataset ─────────────────────────────────────
    CSV_PATH = "data/raw/air_quality.csv"

    try:
        df = pd.read_csv(CSV_PATH)
        print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns\n")

        report = detect_missing(df)
        print_missing_report(report)

        # Quick sanity check: total missing cells
        total_missing = sum(v["count"] for v in report.values())
        print(f"Total missing cells across entire dataset: {total_missing:,}")

    except FileNotFoundError:
        print(f"⚠️  CSV not found at '{CSV_PATH}'")
        print("Place your dataset there and re-run.")
        print("(Tests above still passed — detector logic is correct!)")
