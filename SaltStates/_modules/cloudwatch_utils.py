import boto3

def createLogGroup(logGroupName, region='us-east-1'):
    client = boto3.client('logs', region_name=region)
    try:
        response = client.create_log_group(
            logGroupName=logGroupName
        )
    except Exception as e:
        print(e)
        print(f"Log group {logGroupName} already created")
        return True