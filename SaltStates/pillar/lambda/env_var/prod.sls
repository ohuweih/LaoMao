functions:
  - functionName: NAME-prod-backend-container
    account: 845537639440
    roleArn: arn:aws:iam::123456789:role/RoLeNAME
    image: Image Link
    description: "Back end lambda"
    timeout: 900 #time is in (secs/minutes)
    memorySize: 512 #size in mb
    storageSize: 512
    region: us-east-1
    subnetIds:
      - subnet-1234567891
      - subnet-1234567891
    securityGroupIds:
      - {{ salt['grains.get']('NAME-prod-ecs-fargate-ContainerSecurityGroup') }}
      - {{ salt['grains.get']('NAME-prod-common-scg') }}
    tags: {"Name": "NAME-prod-backend-container", "Environment": "prod", "Project": "LaoMao", "ManagedBy": "Salt"}