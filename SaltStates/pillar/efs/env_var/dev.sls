efsValues:
  - name: NAME-dev
    performanceMode: generalPurpose
    encrypted: False
    backup: False
    fileSystemId:
    subnetId: subnet-123456798
    ipAddress: a ip from the subnet picked. 
    secGrps:
      - {{ salt['grains.get']('NAMEdev-pipeline-test-5') }}
    tags: {"Name": "NAMEdev-salt-test", "vpc": "vpc-123456789", "Environment": "Dev", "Project": "LaoMao", "Manageby": "Salt"}