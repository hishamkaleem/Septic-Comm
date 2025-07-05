import json
import boto3
import uuid
from datetime import datetime

s3 = boto3.client('s3')
bucket_name = 'werldatabucket'

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        timestamp = datetime.utcnow().isoformat()
        body["timestamp"] = timestamp
        filename = f"Sensor_Data_{timestamp}.json"

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
