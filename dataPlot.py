import boto3
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    if col not in ["timestamp", "Tank Depth", "Total Data Usage (MB):"] #Add other columns to exclude if needed
]

# Plot one figure per depth in separate windows
for depth in unique_depths:
    df_depth = df[df["Tank Depth"] == depth]

    # Plot dimensions/title
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.canvas.manager.set_window_title(f"Tank Depth: {depth} cm")

    # Plot each sensor
    for sensor in sensor_columns:
        ax.plot(df_depth["timestamp"], df_depth[sensor], label=sensor)

    # Labels and formatting
    ax.set_title(f"Sensor Data for Tank Depth: {depth} cm")
    ax.set_ylabel("Sensor Values")
    ax.set_xlabel("Time (H:M:S)")
    ax.grid(True)

    # Format x-axis labels
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M:%S"))
    ax.tick_params(axis='x', rotation=45)

    # Make a legend and keep it outside right of the plot
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

    # Padding for legend and bottom tick labels
    fig.subplots_adjust(right=0.8, bottom=0.3)

    plt.show(block=False)
    plt.pause(0.1)

plt.show() # Keep the last plot open (prevents immediate termination of the script)