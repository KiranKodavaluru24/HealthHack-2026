import zipfile
from pathlib import Path
import pandas as pd

ZIP_NAME = "extention+of+z+alizadeh+sani+dataset.zip"

matches = list(Path(".").rglob(ZIP_NAME))
if not matches:
    raise SystemExit(f"Not connected: {ZIP_NAME} not found. Upload it to the Codespace first.")

zip_path = matches[0]
print(f"Found zip: {zip_path.resolve()}")

with zipfile.ZipFile(zip_path) as z:
    names = z.namelist()
    print("Files inside:", names)
    xlsx = next(n for n in names if n.lower().endswith(".xlsx"))
    z.extract(xlsx, "data")

df = pd.read_excel(Path("data") / xlsx, sheet_name=0)
print(f"Connected to the zip file. Loaded {df.shape[0]} patients, {df.shape[1]} columns.")