s3Buckets:
  - name: LaoMao-dev-salt-Finale-Test
    tags: {"Name": "LaoMao-dev-salt", "ManagedBy": "Salt", "Project": "LaoMao", "DELETETHIS": "True", "Environment": "Dev"}
    versioning: Enabled
    loggingBucket: LaoMao-s3-access-logs-salt
    account: 123456798
    functionName: LaoMao-dev-backend-container