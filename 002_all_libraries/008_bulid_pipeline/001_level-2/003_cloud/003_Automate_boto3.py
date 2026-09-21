import boto3
from botocore.exceptions import ClientError, BotoCoreError

client = boto3.client('ses', region_name='us-east-1')

try:
    response = client.send_email(
        Destination={
            'ToAddresses': ['recipient@example.com'],
        },
        Message={
            'Subject': {
                'Data': 'Test Email'
            },
            'Body': {
                'Text': {
                    'Data': 'This is a test email.'
                }
            }
        },
        Source='sender@example.com'
    )
    print(response)
except ClientError as e:
    print(f"Client error: {e.response['Error']['Message']}")
else:
    print("Email sent! Message ID:"),
    print(response['MessageId'])