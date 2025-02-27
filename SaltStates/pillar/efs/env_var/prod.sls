efsValues:
  - name: NAME-prod
    performanceMode: generalPurpose
    encrypted: True
    backup: True
    fileSystemId:
    subnets:
      - subnetId: subnet-123456798
        ipAddress: 127.0.0.1
        secGrps:
          - {{ salt['grains.get']('NAME-prod-common-scg') }}
      - subnetId: subnet-0a3f7d83e051e9605
        ipAddress: 127.0.0.1
        secGrps:
          - {{ salt['grains.get']('NAME-prod-common-scg') }}
    tags:
      - {"Key": "Name", "Value": "NAME-prod"}
      - {"Key": "Environment", "Value": "prod"} 
      - {"Key":"Project", "Value": "LaoMao"} 
      - {"Key":"Manageby", "Value": "Salt"}