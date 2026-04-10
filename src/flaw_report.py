"""
src/flaw_report.py
Data Flaw Hunter — Day 7: Unified Flaw Report Generator
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from detector import detect_missing

# ── Outlier detector (from Day 5) ────────────────────────
def detect_outliers(df, col):
    data = df[col].dropna()
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    iqr_outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
    return len(iqr_outliers)

# ── Main report builder ───────────────────────────────────
def build_flaw_report(df):
    pollutant_cols = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 
                      'NH3', 'CO', 'SO2', 'O3', 'Benzene', 
                      'Toluene', 'Xylene']
    
    rows = []

    # Missing values
    missing_report = detect_missing(df)
    for col, info in missing_report.items():
        if info['severity'] != 'OK':
            rows.append({
                'flaw_type': 'Missing Value',
                'column': col,
                'count': info['count'],
                'severity': info['severity'],
                'severity_score': info['pct']
            })

    # Outliers
    for col in pollutant_cols:
        count = detect_outliers(df, col)
        pct = round(count / len(df) * 100, 2)
        if pct > 20:
            severity = 'CRITICAL'
        elif pct > 10:
            severity = 'HIGH'
        elif pct > 5:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        rows.append({
            'flaw_type': 'Outlier',
            'column': col,
            'count': count,
            'severity': severity,
            'severity_score': pct
        })

    # Format flaw
    rows.append({
        'flaw_type': 'Format',
        'column': 'Date',
        'count': 1,
        'severity': 'LOW',
        'severity_score': 1
    })

    flaw_df = pd.DataFrame(rows)
    flaw_df = flaw_df.sort_values('severity_score', ascending=False)
    return flaw_df


if __name__ == "__main__":
    df = pd.read_csv('data/raw/air_quality.csv')

    print("Building flaw report...")
    flaw_df = build_flaw_report(df)

    # Save CSV
    flaw_df.to_csv('reports/flaw_report.csv', index=False)
    print("✅ Flaw report saved to reports/flaw_report.csv")

    # Print summary
    print(f"\nTotal flaws found: {len(flaw_df)}")
    print(f"CRITICAL: {len(flaw_df[flaw_df['severity']=='CRITICAL'])}")
    print(f"HIGH    : {len(flaw_df[flaw_df['severity']=='HIGH'])}")
    print(f"MEDIUM  : {len(flaw_df[flaw_df['severity']=='MEDIUM'])}")
    print(f"LOW     : {len(flaw_df[flaw_df['severity']=='LOW'])}")
    print("\nTop 5 worst flaws:")
    print(flaw_df.head())