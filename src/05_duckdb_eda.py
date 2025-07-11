import duckdb
import pandas as pd
import logging
from rich.logging import RichHandler
import matplotlib.pyplot as plt

# Setup logging
logging.basicConfig(
    format="{asctime} [{levelname}] {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[RichHandler()],
)

log = logging.getLogger("rich")

# Connect to the DuckDB database
db_file = 'projects.duckdb'
conn = duckdb.connect(db_file)
log.info(f"Connected to DuckDB database at {db_file}")

# Load the data into a pandas DataFrame
df = conn.execute('SELECT * FROM projects').fetchdf()
log.info(f"Loaded {len(df)} rows from the 'projects' table")

# Display the first few rows of the DataFrame
log.info("Displaying the first few rows of the DataFrame:")
print(df.head())

# Summary statistics
log.info("Generating summary statistics:")
print(df.describe(include='all'))

# Check for missing values
log.info("Checking for missing values:")
print(df.isnull().sum())

# Statistics for the 'description' column
log.info("Generating statistics for the 'description' column:")
df['description_length'] = df['description'].apply(len)
description_stats = {
    'count': df['description'].count(),
    'missing': df['description'].isnull().sum(),
    'average_length': df['description_length'].mean(),
    'min_length': df['description_length'].min(),
    'max_length': df['description_length'].max()
}
print(description_stats)

# Percentiles for the 'description' column
percentiles = df['description_length'].quantile([0.25, 0.5, 0.75, 0.95, 0.99])
print("Percentiles for the 'description' column:")
print(percentiles)

# Plot the distribution of the length of 'description'
plt.figure(figsize=(10, 6))
plt.hist(df['description_length'].dropna(), bins=50, edgecolor='k', alpha=0.7)
plt.title('Distribution of Description Lengths')
plt.xlabel('Length of Description')
plt.ylabel('Frequency')
plt.grid(True)

# Save the plot to a file
chart_file = 'description_length_distribution.png'
plt.savefig(chart_file)
log.info(f"Saved the chart to {chart_file}")

# Show a sample of the top 5 URLs with a description length of 0
log.info("Showing a sample of the top 5 URLs with a description length of 0:")
empty_descriptions = df[df['description_length'] == 0]
print(empty_descriptions[['url', 'description']].head(5).to_string(index=False, max_colwidth=None))

# Analyze the 'forma_presentacion' field
forma_presentacion_counts = df['forma_presentacion'].value_counts()

# Plot the distribution of 'forma_presentacion'
plt.figure(figsize=(12, 8))
forma_presentacion_counts.plot(kind='bar', edgecolor='k', alpha=0.7)
plt.title('Distribution of Forma de Presentación')
plt.xlabel('Forma de Presentación')
plt.ylabel('Frequency')
plt.xticks(rotation=45, ha='right')
plt.grid(True)

# Save the plot to a file
forma_presentacion_chart_file = 'forma_presentacion_distribution.png'
plt.savefig(forma_presentacion_chart_file)
log.info(f"Saved the chart to {forma_presentacion_chart_file}")

# Log and print the top 5 most common 'forma_presentacion'
log.info("Top 5 most common 'Forma de Presentación':")
print(forma_presentacion_counts.head(5).to_string())

# Close the DuckDB connection
conn.close()
log.info("Closed DuckDB connection")
