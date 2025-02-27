functions:
  - functionName: NAME-dev-backend-container
    account: 613398752565
    roleArn: arn:aws:iam::123456789:role/RoleNAme
    image: '613398752565.dkr.ecr.us-east-1.amazonaws.com/pe-dev/backend-lambda:latest'
    description: NAME-dev-backend-container
    timeout: 900 #time is in (secs/minutes)
    memorySize: 512 #size in mb
    storageSize: 512
    region: us-east-1
    subnetIds:
      - subnet-1234567894413
      - subnet-12345678943
    securityGroupIds:
      - {{ salt['grains.get']('NAME-dev-common-scg-gitlab-pipeline-deploy') }}
      - {{ salt['grains.get']('NAME-dev-ecs-fargate-LoadBalancerSecurityGroup-gitlab-pipeline-deploy') }}
    tags: {"Name": "NAME-dev-backend-container-gitlab-pipeline", "Environment": "Dev", "Project": "LaoMao", "ManagedBy": "Salt", "DELETETHIS": "True" }