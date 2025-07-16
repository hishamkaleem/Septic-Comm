import boto3
import json
import pandas as pd
import matplotlib.pyplot as plt

AWS_access_key_id = "ABC..."                         #User access key (REPLACE WITH OWN)
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

# Convert timestamp to datetime and sort the DataFrame
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# Plot the data
plt.figure(figsize=(12, 6))
#plt.plot(df["timestamp"], df["Potentiometer"], label="Potentiometer")
plt.plot(df["timestamp"], df["Temperature"], label="Temperature (°C)")

# Add labels and title
plt.xlabel("Timestamp")
plt.ylabel("Sensor Values")
plt.title("Sensor Data Over Time")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


