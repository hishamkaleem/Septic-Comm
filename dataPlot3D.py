import boto3
import json
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import math

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

# Determine sensor columns
known = {"timestamp", "Tank Depth", "Total Data Usage (MB)", "time_offset_sec"}
sensor_cols = [c for c in df.columns if c not in known]
depths = sorted(df["Tank Depth"].unique())

# Subplot layout setup
num_sensors = len(sensor_cols)
cols = 2
rows = math.ceil(num_sensors / cols)

fig = make_subplots(
    rows=rows,
    cols=cols,
    specs=[[{'type': 'scatter3d'}] * cols for _ in range(rows)],
    subplot_titles=sensor_cols
)

# Add traces per sensor and depth
for idx, sensor in enumerate(sensor_cols):
    row = (idx // cols) + 1
    col = (idx % cols) + 1

    for depth in depths:
        df_sub = df[df["Tank Depth"] == depth]
        if df_sub.empty:
            continue

        fig.add_trace(
            go.Scatter3d(
                x=df_sub["time_offset_sec"],
                y=[depth] * len(df_sub),
                z=df_sub[sensor],
                mode="lines+markers",
                name=f"{sensor} @ {depth}cm",
                line=dict(width=2),
                marker=dict(size=3),
                hovertext=df_sub["timestamp"].dt.strftime("%H:%M:%S.%f"),
                hoverinfo="text+name"
            ),
            row=row,
            col=col
        )

# Update each subplot's 3D scene individually
layout_updates = {}
for i in range(1, num_sensors + 1):
    scene_name = "scene" if i == 1 else f"scene{i}"
    layout_updates[scene_name] = dict(
        xaxis=dict(
            title="Time Offset (s)",
            tickmode="auto",
            showgrid=True
        ),
        yaxis=dict(title="Depth (cm)"),
        zaxis=dict(title="Sensor Value"),
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
    )

# Apply layout updates and display
fig.update_layout(
    **layout_updates,
    height=400 * rows,
    width=1000,
    title_text="3D Sensor Readings by Tank Depth (Subplots per Sensor)",
    margin=dict(l=20, r=20, t=50, b=20),
    showlegend=False
)

fig.show()