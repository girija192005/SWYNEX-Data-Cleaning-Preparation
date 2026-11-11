"""
SWYNEX Internship - Task 1: Data Cleaning & Preparation
Dataset: Titanic passenger data (public)
Usage:   python src/clean_titanic.py
"""
import urllib.request
from pathlib import Path
import pandas as pd

URL = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "titanic_raw.csv"
CLEAN = ROOT / "data" / "cleaned" / "titanic_cleaned.csv"
LOG = ROOT / "data" / "cleaned" / "cleaning_log.txt"

log = []
def note(msg):
    print(msg)
    log.append(msg)

def audit(df, title):
    note(f"\n=== {title} ===")
    note(f"Shape: {df.shape}")
    miss = df.isna().sum()
    note("Missing values per column:\n" + miss[miss > 0].to_string())
    note(f"Duplicate rows: {df.duplicated().sum()}")
    note("Data types:\n" + df.dtypes.to_string())

# 1. Load
if not RAW.exists():
    RAW.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(URL, RAW)
df = pd.read_csv(RAW)
audit(df, "BEFORE CLEANING")

# 2. Standardise column names
df.columns = [c.strip().lower() for c in df.columns]
note("\nColumn names standardised to lowercase.")

# 3. Duplicates (full rows, then repeated passenger IDs)
n = len(df)
df = df.drop_duplicates()
df = df.drop_duplicates(subset="passengerid", keep="first")
note(f"Removed {n - len(df)} duplicate records.")

# 4. Inconsistent text values
for col in ["name", "sex", "ticket", "cabin", "embarked"]:
    df[col] = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
df["sex"] = df["sex"].str.lower()
df["embarked"] = df["embarked"].str.upper().map(
    {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"})
note("Trimmed whitespace, lower-cased 'sex', expanded 'embarked' codes to port names.")

# 5. Feature extraction
df["deck"] = df["cabin"].str[0]
df["title"] = df["name"].str.extract(r",\s*([^.]+)\.", expand=False).str.strip()
df["title"] = df["title"].replace({"Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs"})
rare = df["title"].value_counts()[lambda s: s < 10].index
df["title"] = df["title"].replace(dict.fromkeys(rare, "Other"))
note("Extracted 'deck' from cabin and 'title' from name; merged rare titles into 'Other'.")

# 6. Missing values
df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])
df["age"] = df["age"].fillna(df.groupby(["pclass", "sex"])["age"].transform("median"))
df["deck"] = df["deck"].fillna("Unknown")
df = df.drop(columns=["cabin"])
note("Embarked -> mode; Age -> median by (pclass, sex); deck -> 'Unknown'; raw cabin dropped (~77% missing).")

# 7. Data types
df["survived"] = df["survived"].astype("bool")
for col in ["pclass", "sex", "embarked", "deck", "title"]:
    df[col] = df[col].astype("category")
df["age"] = df["age"].round(1)
df["fare"] = pd.to_numeric(df["fare"], errors="coerce")
note("Cast survived->bool; pclass/sex/embarked/deck/title->category; fare->float.")

# 8. Validity checks / outliers
assert df["age"].between(0, 100).all(), "Age out of range"
assert (df["fare"] >= 0).all(), "Negative fare"
q1, q3 = df["fare"].quantile([.25, .75])
note(f"Fare outliers (>Q3+3*IQR) flagged but kept: {(df['fare'] > q3 + 3*(q3-q1)).sum()}")

audit(df, "AFTER CLEANING")
CLEAN.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(CLEAN, index=False)
LOG.write_text("\n".join(log))
note(f"\nSaved: {CLEAN}")
