import boto3

def create_ecr(repoName):
    client = boto3.client('ecr', region_name='us-east-1')
    try:
        response = client.create_repository(
            repositoryName=repoName,
            imageTagMutability='MUTABLE',
            imageScanningConfiguration={
                'scanOnPush': True
            },
            encryptionConfiguration={
                'encryptionType': 'AES256'
            }
        )
    except Exception as e:
        print(e)
        print(f"Repo {repoName} already created")
        return True
