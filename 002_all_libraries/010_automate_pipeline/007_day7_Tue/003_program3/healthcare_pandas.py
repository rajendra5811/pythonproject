from pathlib import Path
import pandas as pd


def run_pandas_pipeline():
  input_file = Path("healthcare_input.json")

  if not input_file.exists():
    print(f"Error: Could not find {input_file}. Please create the input file first.")
    return

  # 1. Ingest JSON dataset directly into a Pandas DataFrame
  df = pd.read_json(input_file)
  print(f"Loaded {len(df)} raw records into Pandas.")

  # 2. Validate MRN format using regex pattern (e.g., MRN-102938)
  mrn_pattern = r"^MRN-\d{6}$"
  valid_mask = df["mrn"].str.match(mrn_pattern, na=False)

  # Separate valid records from malformed ones
  valid_df = df[valid_mask].copy()
  invalid_df = df[~valid_mask]

  if not invalid_df.empty:
    print(f"⚠️ Warning: Dropped {len(invalid_df)} malformed record(s) with invalid MRNs.")

  # 3. Transform Data: Apply Triage Status vector calculation
  # CRITICAL if heart_rate > 120 or < 50, otherwise STABLE
  valid_df["triage_status"] = "STABLE"
  valid_df.loc[
      (valid_df["heart_rate"] > 120) | (valid_df["heart_rate"] < 50),
      "triage_status",
  ] = "CRITICAL"

  # Optional: Calculate BMI if weight and height columns exist
  if "weight_kg" in valid_df.columns and "height_m" in valid_df.columns:
    valid_df["bmi"] = round(valid_df["weight_kg"] / (valid_df["height_m"] ** 2), 1)

  # 4. Persistence (No SQL! Saving directly to a clean CSV report)
  output_file = Path("processed_healthcare_report.csv")
  valid_df.to_csv(output_file, index=False)

  print(f"\nPipeline complete! Successfully processed and saved to '{output_file}'.")
  print("\n--- Final Clean Data Preview ---")
  print(valid_df[["mrn", "patient_name", "heart_rate", "triage_status"]])


if __name__ == "__main__":
  run_pandas_pipeline()