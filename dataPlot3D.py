import boto3 #Need to pip
import json
import pandas as pd #Ned to pip
import numpy as np #Need to pip
import plotly.graph_objs as go #Need to pip
import plotly.io as pio #Need to pip
from datetime import datetime
import webbrowser
import os

pio.renderers.default = "json" #Renderer for Plotly

AWS_access_key_id = "ABC..."     #User access key (REPLACE WITH OWN)
AWS_secret_access_key = "XYZ..." #User secret access key (REPLACE WITH OWN)

bucket_name = "werldatabucket"  #Bucket name (REPLACE WITH OWN)

# AWS S3 Client Initialization
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_access_key_id,
    aws_secret_access_key=AWS_secret_access_key
)

# Read JSON files from S3
objects = s3.list_objects_v2(Bucket=bucket_name)
if "Contents" not in objects:
    print("No data files found.")
    exit()

data_list = []
for obj in objects["Contents"]:
    key = obj["Key"]
    if key.endswith(".json"):
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response["Body"].read()
        json_data = json.loads(content)
        data_list.append(json_data)

# Convert to DataFrame
df = pd.DataFrame(data_list)
df.columns = [c.strip() for c in df.columns]
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["timestamp", "Tank Depth"])

# Create time offset in seconds from the start
start_time = df["timestamp"].min()
df["time_offset_sec"] = (df["timestamp"] - start_time).dt.total_seconds()

# Format time offset for hover labels (e.g., 1 hr 2 min 3 s)
def format_elapsed(seconds):
    seconds = int(seconds)
    hrs, remainder = divmod(seconds, 3600)
    mins, secs = divmod(remainder, 60)
    parts = []
    if hrs > 0:
        parts.append(f"{hrs}h")
    if mins > 0:
        parts.append(f"{mins}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)

df["time_label"] = df["time_offset_sec"].apply(format_elapsed) #Apply formatted time label 

# Determine sensor columns
known = {"timestamp", "Tank Depth", "Total Data Usage (MB)", "time_offset_sec", "time_label"}
sensor_cols = [c for c in df.columns if c not in known]
depths = sorted(df["Tank Depth"].unique())

allFigs = ""

#Plot figure per sensor in 3D
for sensor in sensor_cols:
    fig = go.Figure()

    for depth in depths:
        df_sub = df[df["Tank Depth"] == depth]
        if df_sub.empty:
            continue
        # Add a trace for each depth
        fig.add_trace(
            go.Scatter3d(
                x=df_sub["time_offset_sec"],
                y=[depth] * len(df_sub),
                z=df_sub[sensor],
                mode="lines+markers",
                name=f"{sensor} @ {depth}cm",
                line=dict(width=2),
                marker=dict(size=3),
                # Hover text showing elapsed time, timestamp, depth, and sensor value
                hovertext=(
                    "Elapsed: " + df_sub["time_label"] +
                    "<br>Time: " + df_sub["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S") +
                    "<br>Depth (cm): " + df_sub["Tank Depth"].astype(str) +
                    "<br>Value: " + df_sub[sensor].astype(str)
                ),
                hoverinfo="text"
            )
        )

    # Define custom X-axis ticks (max 7)
    x_min = df["time_offset_sec"].min()
    x_max = df["time_offset_sec"].max()
    num_ticks = min(7, len(df))  # fallback if dataset is small
    tickvals = np.linspace(x_min, x_max, num_ticks)
    ticktext = [format_elapsed(t) for t in tickvals]

    # Update layout
    fig.update_layout(
        title=f"{sensor} vs Time/Depth (3D)",
        scene=dict(
            # Set axis titles
            xaxis=dict(
                title="Elapsed Time",
                # X-axis ticks using custom values
                tickvals=tickvals.tolist(),
                ticktext=ticktext,
                showgrid=True,
                autorange="reversed"
            ),
            yaxis=dict(title="Tank Depth (cm)", autorange="reversed", showgrid=True),
            zaxis=dict(title="Sensor Value", autorange=True, showgrid=True),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        # Set margins for better visibility
        margin=dict(l=20, r=20, t=50, b=20),
        height=600,
        width=800,
        showlegend=True
    )
    # Convert to HTML and append to the list
    allFigs += pio.to_html(fig, full_html=False, include_plotlyjs=True) + "<hr>" 
    
# Create output directory if it doesn't exist
output_dir = "Generated Plots"
os.makedirs(output_dir, exist_ok=True)

# Timestamped filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"3DPLOT_{timestamp}.html"
output_path = os.path.join(output_dir, filename)

# Wrap all HTML figures in a single HTML document (very basic formatting)
final_html = f"""
<html>
<head>
    <title>Sensor Plots (3D)</title>
    <style>
        body {{
            font-family: sans-serif;
            padding: 20px;
        }}
        hr {{
            margin: 60px 0;
            border: none;
            border-top: 1px solid #ccc;
        }}
    </style>
</head>
<body>
    <h1>3D Plots for All System Sensors</h1>
    {allFigs}
</body>
</html>
"""

# Write HTML to file
with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_html)

# Open the generated HTML file in chrome (CHANGE TO OWN BROWSER PATH IF NEEDED)
html_path = os.path.abspath(output_path)
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
webbrowser.get(chrome_path).open(f"file://{html_path}")