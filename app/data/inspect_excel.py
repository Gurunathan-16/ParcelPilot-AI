import pandas as pd
from pathlib import Path

FILE_PATH = Path("data/ParcelPilot_Assessment_Data.xlsx")

print("=" * 60)
print("PARCELPILOT EXCEL INSPECTION")
print("=" * 60)

excel_file = pd.ExcelFile(FILE_PATH)

print("\nSHEETS FOUND:")
for sheet in excel_file.sheet_names:
    print(f"  - {sheet}")

print("\n" + "=" * 60)
print("COLUMN INFORMATION")
print("=" * 60)

for sheet in excel_file.sheet_names:
    df = pd.read_excel(FILE_PATH, sheet_name=sheet)

    print(f"\n[{sheet}]")
    print(f"Rows: {len(df)}")
    print("Columns:")

    for column in df.columns:
        print(f"  - {column}")