
import boto3
from botocore.exceptions import ClientError

# Replace with your region
region = 'us-east-1'  # or 'ap-south-1', 'us-west-2', etc.
bucket_name = 'tejaswi-bucket-2002'  # Make sure this is unique globally

# Initialize session
session = boto3.session.Session(region_name=region)
s3 = session.client('s3')

try:
    if region == 'us-east-1':
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
    print(f'✅ Bucket "{bucket_name}" created successfully in {region}')
except ClientError as e:
    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print(f'ℹ️ Bucket "{bucket_name}" already exists and is owned by you.')
    else:
        print(f'❌ Failed to create bucket: {e}')
