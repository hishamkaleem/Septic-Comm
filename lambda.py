import json
import boto3
import uuid
import requests
from datetime import datetime

s3 = boto3.client("s3")
bucket_name = "werldatabucket"

clientID = "ABC..."
clientSecret = "XYZ..."
project_uid = "app:ABC..."
device_uid = "dev:XYZ..."

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

    device_url = f"https://api.notefile.net/v1/projects/{project_uid}/devices/{device_uid}"
    device_resp = requests.get(
        device_url,
        headers={"Authorization": f"Bearer {token}"}
    )
    device_resp.raise_for_status()
    device_info = device_resp.json()

    usage_bytes = (device_info.get("cellular_usage"))[0].get('lifetimeUsed')
    usage_mb = round(usage_bytes/1000000, 2)

    return usage_mb

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        timestamp = datetime.utcnow().isoformat()
        body["timestamp"] = timestamp
        filename = f"Sensor_Data_{timestamp}.json"

        dataUsage = notecardDataReq()
        body["Total Data Usage (MB):"] = dataUsage

        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=json.dumps(body),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data with timestamp saved to S3'})
        }

    except Exception as e:
        print("Lambda error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

