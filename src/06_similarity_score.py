import duckdb
import pandas as pd
import logging
from rich.logging import RichHandler
from fuzzywuzzy import fuzz
import geopandas as gpd

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
db_file = "projects.duckdb"
conn = duckdb.connect(db_file)
log.info(f"Connected to DuckDB database at {db_file}")

# Load the data into a pandas DataFrame
df = conn.execute("SELECT * FROM projects").fetchdf()
log.info(f"Loaded {len(df)} rows from the 'projects' table")

# Define the target strings
target_strings = ["h2v", "hidrogeno verde"]


# Function to calculate similarity score
def calculate_similarity(text: str, target_strings):
    text = text.lower()
    max_score = 0
    for target in target_strings:
        score = fuzz.partial_ratio(text, target)
        if score > max_score:
            max_score = score
    return max_score


# Calculate similarity scores
df["similarity_score"] = df.apply(
    lambda row: calculate_similarity(
        f"{row['project_name']} {row['description']}", target_strings
    ),
    axis=1,
)

# Load the cleaned GeoDataFrame
gdf_cleaned = gpd.read_file("./DATA/proyectos_cleaned.gpkg")
log.info(f"Loaded {len(gdf_cleaned)} rows from 'proyectos_cleaned.gpkg'")

# Merge the DataFrame with the GeoDataFrame by URL
merged_df = pd.merge(
    df, gdf_cleaned, left_on="url", right_on="constructed_link", how="left"
)
log.info(f"Merged DataFrame has {len(merged_df)} rows")

# Check for any URLs in the DuckDB DataFrame that do not have a corresponding match in the GeoDataFrame
missing_urls = merged_df[merged_df["geometry"].isnull()]["url"]
if not missing_urls.empty:
    log.warning(
        f"The following URLs do not have a corresponding match in 'proyectos_cleaned.gpkg':\n{missing_urls.to_string(index=False)}"
    )
else:
    log.info("All URLs have a corresponding match in 'proyectos_cleaned.gpkg'")

# Save the merged DataFrame to a new .gpkg file
output_file = "./DATA/proyectos_with_similarity.gpkg"
merged_gdf = gpd.GeoDataFrame(merged_df, geometry="geometry")
merged_gdf.to_file(output_file, driver="GPKG")
log.info(f"Saved the merged DataFrame with similarity scores to {output_file}")

# Close the DuckDB connection
conn.close()
log.info("Closed DuckDB connection")
