# This file contains utilities for downloading data or doing miscelanious tasks.
import geopandas as gpd


def main():
    url = "https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_CHL.gpkg"
    try:
        gdf = gpd.read_file(url, layer="ADM_ADM_3")
        # save layer "ADM_ADM_3"
        gdf.to_file("./DATA/communes.gpkg", driver="GPKG")

        print("File saved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


# main guard
if __name__ == "__main__":
    main()
