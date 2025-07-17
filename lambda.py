import json
import boto3
import requests
from datetime import datetime, timedelta

s3 = boto3.client("s3")
bucket_name = "werldatabucket" # Bucket name (REPLACE WITH OWN)

clientID = "ABC..." # User client ID (REPLACE WITH OWN)
clientSecret = "XYZ..." # User client secret (REPLACE WITH OWN)
project_uid = "app:ABC..." # Project UID (REPLACE WITH OWN)
device_uid = "dev:XYZ..." # Device UID (REPLACE WITH OWN)

# Function to request data usage from Notecard
def notecardDataReq():
    token_url = "https://notehub.io/oauth2/token"
    token_resp = requests.post(
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": clientID,
            "client_secret": clientSecret
        }
    )
    token_resp.raise_for_status()
    token = token_resp.json()["access_token"]

    # Get device information to retrieve billed data usage
    device_url = f"https://api.notefile.net/v1/projects/{project_uid}/devices/{device_uid}"
    device_resp = requests.get(
        device_url,
        headers={"Authorization": f"Bearer {token}"}
    )
    device_resp.raise_for_status()
    device_info = device_resp.json()

    # Extract lifetime cellular data usage in bytes and convert to MB
    usage_bytes = (device_info.get("cellular_usage"))[0].get('lifetimeUsed')
    usage_mb = round(usage_bytes/1000000, 2)

    return usage_mb

# Lambda handler function
def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        # Add timestamp to the body
        # Use UTC time minus 4 hours to match the original timestamp format (for Canada)
        timestamp = (datetime.utcnow() - timedelta(hours=4)).isoformat()
        body["timestamp"] = timestamp
        
        # Save the body to S3 with the timestamp in the filename
        filename = f"Sensor_Data_{timestamp}.json"

        # Request data usage from Notecard via the function
        dataUsage = notecardDataReq()
        body["Total Data Usage (MB):"] = dataUsage

        # Upload the JSON data to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=json.dumps(body),
            ContentType='application/json'
        )

        # Log the successful upload
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data with timestamp saved to S3'})
        }

    # Handle any exceptions that occur
    except Exception as e:
        print("Lambda error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

