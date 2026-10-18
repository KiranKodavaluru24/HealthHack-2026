import zipfile
from pathlib import Path
import pandas as pd

ZIP_NAME = "extention+of+z+alizadeh+sani+dataset.zip"

# Find dataset zip
matches = list(Path(".").rglob(ZIP_NAME))

if not matches:
    raise SystemExit(
        f"Not connected: {ZIP_NAME} not found. Upload it to the Codespace first."
    )

zip_path = matches[0]
print(f"Found zip: {zip_path.resolve()}")

# Extract Excel file
with zipfile.ZipFile(zip_path) as z:
    names = z.namelist()

    print("\nFiles inside ZIP:")
    for name in names:
        print(f"  - {name}")

    xlsx = next(n for n in names if n.lower().endswith(".xlsx"))
    z.extract(xlsx, "data")

# Load dataset
df = pd.read_excel(Path("data") / xlsx, sheet_name=0)

print("\n====================================")
print(" DATASET CONNECTION SUCCESSFUL")
print("====================================")

print(f"Patients loaded : {df.shape[0]}")
print(f"Columns loaded  : {df.shape[1]}")

# CAD vs Normal summary
if "Cath" in df.columns:

    cad_count = (df["Cath"].astype(str).str.strip() == "CAD").sum()
    normal_count = (df["Cath"].astype(str).str.strip() == "Normal").sum()

    print("\nPatient Distribution")
    print("--------------------")
    print(f"CAD Patients    : {cad_count}")
    print(f"Normal Patients : {normal_count}")

# Important health variables
HEALTH_VARIABLES = {
    "BMI": "Body Mass Index (weight relative to height)",
    "FBS": "Fasting Blood Sugar",
    "LDL": "Bad Cholesterol",
    "HDL": "Good Cholesterol",
    "TG": "Triglycerides (blood fat)",
    "BP": "Blood Pressure",
    "EF-TTE": "Heart Pumping Efficiency (Ejection Fraction)"
}

print("\nKey Health Variables")
print("--------------------")

for col, meaning in HEALTH_VARIABLES.items():
    if col in df.columns:
        print(f"{col:<8} -> {meaning}")

# Basic statistics
print("\nSelected Dataset Statistics")
print("---------------------------")

for col in ["Age", "BMI", "FBS", "LDL", "HDL", "TG"]:
    if col in df.columns:
        print(
            f"{col:<5} "
            f"Mean={df[col].mean():.1f} "
            f"Min={df[col].min():.1f} "
            f"Max={df[col].max():.1f}"
        )

# Missing values
missing_values = df.isna().sum().sum()

print("\nData Quality Check")
print("------------------")
print(f"Missing values: {missing_values}")

# Preview of dataset
print("\nFirst 3 Records")
print("---------------")
print(df.head(3).to_string(index=False))

print("\nReady for model training and medical-term explanations.")