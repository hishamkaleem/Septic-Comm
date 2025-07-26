import boto3 #Need to pip
import json
import pandas as pd #Need to pip
import plotly.graph_objs as go #Need to pip
import os
import subprocess
import tempfile
from datetime import datetime

AWS_access_key_id = "ABC..."     #User access key (REPLACE WITH OWN)
AWS_secret_access_key = "XYZ..." #User secret access key (REPLACE WITH OWN)

bucket_name = "werldatabucket"  #Bucket name (REPLACE WITH OWN)

#Client initialization
s3 = boto3.client( 
    "s3",
    aws_access_key_id=AWS_access_key_id,
    aws_secret_access_key=AWS_secret_access_key
)

# List and read all JSON files from the S3 bucket
objects = s3.list_objects_v2(Bucket=bucket_name)
if "Contents" not in objects:
    print("No data files found.")
    exit()

# Initialize a list to hold the data from all JSON files
data_list = []

# Loop through each object in the bucket and append the data to the list
for obj in objects["Contents"]:
    key = obj["Key"]
    if key.endswith(".json"):
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response["Body"].read()
        json_data = json.loads(content)
        data_list.append(json_data)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data_list)

# Clean column names and convert timestamps
df.columns = [col.strip() for col in df.columns]
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Reverse depth order so lowest opens last
unique_depths = sorted(df["Tank Depth"].unique(), reverse=True)

# Creating a list of sensor columns
sensor_columns = [
    col for col in df.columns
    if col not in ["timestamp", "Tank Depth", "Total Data Usage (MB)"] #Add other columns to exclude if needed
]

# Create a 2D plot for each sensor
for sensor in sensor_columns:
    fig = go.Figure()
    # Plot one line per depth for particular sensor
    for depth in unique_depths:
        df_depth = df[df["Tank Depth"] == depth].copy()
        fig.add_trace(go.Scatter(
            x=df_depth["timestamp"],
            y=df_depth[sensor],
            mode="lines",
            name=f"{depth} cm",
           hovertemplate = f"Depth: {depth} cm   Value: " + "%{y}<extra></extra>"
        ))

    # Style and layout of the plot
    fig.update_layout(
        title=f"{sensor} vs Time (2D)",
        xaxis_title="Time",
        yaxis_title=f"{sensor} Value",
        hovermode="x",
        margin=dict(t=60, r=20, b=60, l=50),
        height=500
    )
    
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe" # Path to Chrome executable (CHANGE IF NEEDED)
    
    # ****** Temporary file handling (COMMENT OUT IF WANTING TO SAVE PLOTS) ******
    
    # Create a temporary file to save the plot
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        tmp_path = tmp_file.name
        fig.write_html(tmp_path)

    # Open the plot in a new Chrome window
    subprocess.Popen([
        chrome_path,
        "--new-window",
        os.path.abspath(tmp_path)
    ])
    
    # ****************************************************************************

    # ******* UNCOMMENT IF WANTING TO DOWNLOAD AND SAVE PLOTS ***********
    
    # # Create a directory to save the plots
    # base_dir = "Generated 2D Plots"
    # os.makedirs(base_dir, exist_ok=True)
    
    # # Save in sensor-named directory
    # sensor_dir = os.path.join(base_dir, sensor.replace(" ", "_"))
    # os.makedirs(sensor_dir, exist_ok=True)

    # timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Timestamp for filename
    # html_path = os.path.join(sensor_dir, f"2DPLOT_{timestamp_str}.html")
    # fig.write_html(html_path)
    # subprocess.Popen([chrome_path, "--new-window", os.path.abspath(html_path)]) # Open in new Chrome window
    
    # ********************************************************************
