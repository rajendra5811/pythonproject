import boto3

# Create an S3 client
s3_client = boto3.client('s3',
                          access_key_id='YOUR_ACCESS_KEY', 
                          secret_access_key='YOUR_SECRET_KEY',
                          region_name='YOUR_REGION')

#creation of bucket
response = s3_client.create_bucket(Bucket='my-new-bucket', 
                                   CreateBucketConfiguration={
                                       'LocationConstraint': 'YOUR_REGION'})
print("Bucket created:", response)


# Upload a file to the bucket
response = s3_client.put_object(
                                Body = open('index.py', 'r').read(), 
                                Bucket ='my-new-bucket',
                                Key = 'index.py')
print("File uploaded:", response)

#download the file from the bucket
response = s3_client.get_object(Bucket='my-new-bucket', Key='index.py')
print("File downloaded:", response)