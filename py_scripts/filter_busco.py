import pandas as pd

# Load the CSV file
file_path = '/zhome/85/8/203063/a3_fungi/data_out/busco_results_cleaned.csv'
busco_data = pd.read_csv(file_path)

# Display the first few rows of the dataframe
print(busco_data.head())

# Filter the dataframe to keep only rows where 'complete_buscos' is 600 or more
filtered_data = busco_data[busco_data['complete_buscos'] >= 600]

# Display the first few rows of the filtered dataframe
print(filtered_data.head())

print(f"Original dataframe shape: {busco_data.shape}")
print(f"Filtered dataframe shape: {filtered_data.shape}")

# Save the filtered dataframe to a new CSV file
output_file_path = '/zhome/85/8/203063/a3_fungi/data_out/busco_results_600.csv'
filtered_data.to_csv(output_file_path, index=False)