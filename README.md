# SWYNEX Data Cleaning & Preparation (Task 1)

Cleaning of the public **Titanic passenger dataset** using Python (pandas).

- Source: https://github.com/datasciencedojo/datasets/blob/master/titanic.csv
- Raw rows: 891 | Cleaned rows: 891 | Columns: 12 -> 13

## Project structure
```
data/raw/titanic_raw.csv          original, untouched
data/cleaned/titanic_cleaned.csv  cleaned output
data/cleaned/cleaning_log.txt     before/after audit log
src/clean_titanic.py              full cleaning script
```

## How to run
```bash
pip install -r requirements.txt
python src/clean_titanic.py
```

## Issues found and fixes applied
| Issue | Where | Fix |
|---|---|---|
| Missing values | `Age` (~20%) | Filled with median age grouped by class and sex |
| Missing values | `Embarked` (2) | Filled with most frequent port |
| Missing values | `Cabin` (~77%) | Extracted `deck` letter, filled gaps with "Unknown", dropped raw column |
| Duplicates | whole rows and `PassengerId` | Checked and removed (0 found in the original file; check is built in) |
| Inconsistent values | `Sex`, text columns, `Embarked` codes | Trimmed whitespace, lower-cased `sex`, mapped S/C/Q to full port names |
| Inconsistent values | `Name` titles (Mlle, Ms, Mme, rare titles) | Extracted `title`; merged variants and rare titles |
| Wrong data types | `Survived`, `Pclass`, categorical fields | Converted to bool / category |
| Column names | mixed case | Standardised to lowercase |
| Outliers | `Fare` | Flagged with 3x IQR rule; kept because they are real first-class fares |

## Key learnings
- Never drop missing data blindly; group-wise imputation keeps more signal than a global mean.
- Keep the raw file untouched and log every change so the cleaning is reproducible.
