import os
import geopandas as gpd
import pandas as pd

# Path to the directory containing the shapefile
shapefile_dir = r"C:\Users\jjepleting\Downloads\Roads"

# Read the shapefile
roads = gpd.read_file(os.path.join(shapefile_dir, "Roads.shp"))

# Convert polygons to LineStrings
roads['geometry'] = roads['geometry'].boundary

# Create an empty DataFrame to store the network data
network_data = pd.DataFrame(columns=['start_node_x', 'start_node_y', 'end_node_x', 'end_node_y', 'length'])

# Populate the DataFrame with edge data
for index, row in roads.iterrows():
    if row['geometry'].geom_type == 'LineString':
        start_node_x, start_node_y = row['geometry'].coords[0]
        end_node_x, end_node_y = row['geometry'].coords[-1]
        length = row['geometry'].length
        new_row = {'start_node_x': start_node_x, 
                   'start_node_y': start_node_y,
                   'end_node_x': end_node_x,
                   'end_node_y': end_node_y,
                   'length': length}
        network_data = pd.concat([network_data, pd.DataFrame([new_row])], ignore_index=True)

# Save the network data to a CSV file
network_data.to_csv(os.path.join(r"C:\Users\jjepleting\Documents", "network_data.csv"), index=False)
