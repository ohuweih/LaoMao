import boto3

def put_bucket_notification(Bucket, lambdaArn, region='us-east-1'):
    client= boto3.client('s3', region_name=region)
    response = client.put_bucket_notification_configuration(
        Bucket=Bucket,
        NotificationConfiguration={
            'LambdaFunctionConfigurations': [
                {
                    'Id': 'NewObjectCreated',
                    'LambdaFunctionArn': lambdaArn,
                    'Events': [
                        's3:ObjectCreated:*'
                        ]
                }
            ]
        }
    )
    print("Created")
    return response