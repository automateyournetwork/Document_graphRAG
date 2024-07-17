import os
import pandas as pd
import csv

# Define the directory containing Parquet files
parquet_dir = './ragtest/output/output/artifacts'
csv_dir = '/var/lib/neo4j/import/'

# Function to clean and properly format the string fields
def clean_quotes(value):
    if isinstance(value, str):
        # Strip leading/trailing spaces
        value = value.strip()
        # Escape double quotes by doubling them
        value = value.replace('"', '""')
        # Ensure proper quoting for fields with commas, newlines, or quotes
        if ',' in value or '"' in value or '\n' in value:
            value = f'"{value}"'
    return value

# Convert all Parquet files to CSV
for file_name in os.listdir(parquet_dir):
    if file_name.endswith('.parquet'):
        parquet_file = os.path.join(parquet_dir, file_name)
        csv_file = os.path.join(csv_dir, file_name.replace('.parquet', '.csv'))
        
        # Load the Parquet file
        df = pd.read_parquet(parquet_file)
        
        # Clean quotes in string fields
        for column in df.select_dtypes(include=['object']).columns:
            df[column] = df[column].apply(clean_quotes)
        
        # Save to CSV
        df.to_csv(csv_file, index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar='"', escapechar='\\')
        print(f"Converted {parquet_file} to {csv_file} successfully.")

print("All Parquet files have been converted to CSV.")
