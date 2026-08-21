import boto3

s3 = boto3.client(
    "s3",
    region_name="ap-south-1"
)

bucket_name = "my-student-data-pipeline-2026"

s3.upload_file(
    "data/raw/students.json",
    bucket_name,
    "raw/students.json"
)

print("File uploaded successfully")