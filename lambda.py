#AWS lambda function to save to S3 bucket

import json
import boto3
import uuid
from datetime import datetime

s3 = boto3.client('s3')
bucket_name = ''  # Replace with own bucket

def lambda_handler(event, context):
    timestamp = datetime.utcnow().isoformat()
    filename = f"Sensor_Data_{timestamp}_{uuid.uuid4().hex}.json"
    
    # Upload full Notehub event to S3
    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=json.dumps(event), 
        ContentType='application/json'
    )
    
    return {
        'statusCode': 200,
        'body': 'Data saved to Werl Bucket'
    }
