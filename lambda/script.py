import json
import os
import boto3
import urllib.request
import urllib.error
import base64

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs', region_name='us-east-1')

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

def lambda_handler(event, context):
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    image_key = record['s3']['object']['key']

    # Download image from S3
    response = s3_client.get_object(Bucket=bucket, Key=image_key)
    image_bytes = response['Body'].read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    # Call Gemini API
    prompt = (
        "This is a parking lot image. Count the number of occupied and free parking slots. "
        "Reply ONLY in JSON format like: {\"occupied\": 3, \"free\": 5}"
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}}
            ]
        }]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            # Extract JSON from response
            text = text.strip().strip('```json').strip('```').strip()
            inference = json.loads(text)
    except Exception as e:
        print(f"Gemini API error: {e}")
        inference = {"occupied": 0, "free": 0}

    # Publish to SQS
    message = {
        "image_key": image_key,
        "occupied": inference.get("occupied", 0),
        "free": inference.get("free", 0)
    }
    sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    print(f"Processed {image_key}: {message}")
    return {"statusCode": 200, "body": json.dumps(message)}