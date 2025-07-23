import boto3
import json
import pandas as pd
import plotly.graph_objs as go

AWS_access_key_id = "ABC..."     #User access key (REPLACE WITH OWN)
AWS_secret_access_key = "XYZ..." #User secret access key (REPLACE WITH OWN)

bucket_name = "werldatabucket"  #Bucket name (REPLACE WITH OWN)

# Client initialization
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
df.columns = [c.strip() for c in df.columns]
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["timestamp", "Tank Depth"])

# Seperate known columns (non Z-axis) and sort unique depths
known = {"timestamp", "Tank Depth", "Total Data Usage (MB)"}
sensor_cols = [c for c in df.columns if c not in known]
depths = sorted(df["Tank Depth"].unique())

# Create a 3D plot
fig = go.Figure()

# Cycle through sensors and depths
for sensor in sensor_cols:
    for depth in depths:
        # Filter data for the current depth
        df_sub = df[df["Tank Depth"] == depth]
        if df_sub.empty:
            continue
        # Add a line for the current sensor at the current depth
        fig.add_trace(
            go.Scatter3d(
                x=df_sub["timestamp"],
                y=[depth] * len(df_sub),
                z=df_sub[sensor],
                mode="lines+markers",
                name=f"{sensor} @ {depth}cm",
                line=dict(width=3),
                marker=dict(size=2),
            )
        )

# Set layout properties
fig.update_layout(
    title="Sensor Data for All Depths (3D)",
    scene=dict(
        xaxis=dict(title="Time"),
        yaxis=dict(title="Depth (cm)"),
        zaxis=dict(title="Sensor Value"),
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    #Create a legend
    legend=dict(itemsizing="constant", bgcolor="rgba(0,0,0,0)")
)
#Show plot
fig.show()