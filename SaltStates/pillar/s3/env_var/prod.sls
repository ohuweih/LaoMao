s3Buckets:
  - name: LaoMao-prod
    tags: {"Name": "LaoMao-prod", "ManagedBy": "Salt", "Project": "LaoMao", "Environment": "prod"}
    versioning: Enabled
    loggingBucket: LaoMao-prod-s3-access-logs
    functionName: LaoMao-prod-backend-container
    roleArn: {{ salt['grains.get']('LaoMao-prod-backend-container') }}