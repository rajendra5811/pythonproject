import boto3
from datetime import datetime, timezone, timedelta

def remove_old_snapshots():
    ec2 = boto3.client('ec2', region_name='us-east-1')

    response = ec2.describe_snapshots(OwnerIds=['self'])
    snapshots = response['Snapshots']

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    old_snapshots = [snap for snap in snapshots if snap['StartTime'] < thirty_days_ago]
    old_snapshots.sort(key=lambda x: x['StartTime'])    
    for snapshot in old_snapshots:
        ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
        print(f"Deleted snapshot: {snapshot['SnapshotId']} created on {snapshot['StartTime']}")

if __name__ == "__main__":
    remove_old_snapshots()