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
    if col not in ["timestamp", "Tank Depth", "Total Data Usage (MB)"] #Add other columns to exclude if needed
]

# Plot one figure per depth in separate windows
for depth in unique_depths:
    df_depth = df[df["Tank Depth"] == depth].copy()
    
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.canvas.manager.set_window_title(f"Tank Depth: {depth} cm")

    for sensor in sensor_columns:
        ax.plot(range(len(df_depth)), df_depth[sensor], label=sensor)

    N = max(1, len(df_depth) // 10)  # Adjust 10 to control how many labels are shown

    tick_indices = list(range(0, len(df_depth), N))
    tick_labels = [df_depth["timestamp"].iloc[i].strftime("%b %d\n%H:%M") for i in tick_indices]

    # Set x-ticks to evenly spaced indices
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=9)
    ax.set_title(f"Sensor Data for Tank Depth: {depth} cm (2D)")
    ax.set_ylabel("Sensor Values")
    ax.set_xlabel("Time")
    ax.grid(True)

    # Add legend outside the plot area
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))
    fig.subplots_adjust(right=0.8, bottom=0.3)

    plt.show(block=False)
    plt.pause(0.1)

plt.show() # Keep the last plot open (prevents immediate termination of the script)