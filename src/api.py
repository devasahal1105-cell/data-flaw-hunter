"""
src/api.py
Data Flaw Hunter — Day 12: FastAPI
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pandas as pd
import io
import sys
import os

sys.path.append(os.path.dirname(__file__))
from detector import detect_missing

app = FastAPI(title="Data Flaw Hunter API")

# ── Helper ───────────────────────────────────
def detect_outliers_count(df, col):
    data = df[col].dropna()
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    return int(len(df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]))

# ── Route 1: Analyze any CSV ─────────────────
@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    missing_report = detect_missing(df)
    
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    outlier_report = {
        col: detect_outliers_count(df, col)
        for col in numeric_cols
    }
    
    return {
        "shape": {"rows": df.shape[0], "cols": df.shape[1]},
        "missing": missing_report,
        "outliers": outlier_report,
        "total_missing_cells": int(df.isnull().sum().sum())
    }

# ── Route 2: Summary of air quality dataset ──
@app.get("/api/summary")
def summary():
    return {
        "dataset": "India Air Quality",
        "raw_shape": {"rows": 29531, "cols": 16},
        "clean_shape": {"rows": 29531, "cols": 16},
        "missing_before": 88488,
        "missing_after": 0,
        "outliers_fixed": 20853,
        "improvement": "100%",
        "critical_columns": ["Xylene (61%)", "PM10 (38%)", "NH3 (35%)"]
    }

# ── Route 3: Health check ─────────────────────
@app.get("/")
def root():
    return {"message": "Data Flaw Hunter API is live! 🚀"}