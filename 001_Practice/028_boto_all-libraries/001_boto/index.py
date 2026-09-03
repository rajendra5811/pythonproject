import boto3

#create an object for the S3 service
s3_client = boto3.client('s3', region_name='ap-south-1'
                         aws_access_key_id='YOUR_ACCESS_KEY',
                         aws_secret_access_key='YOUR_SECRET_KEY')

# create a bucket

response = s3_client.create_bucket(
    ACL`='private'|'public-read'|'public-read-write'|'authenticated-read',
    Bucket ='string`
    CreateBucketConfiguration = {
        'LocationConstraint': 'ap-south-1'},
        GrantFullControl='string',
        ObjectLockEnabledForBucket=True|False
)
