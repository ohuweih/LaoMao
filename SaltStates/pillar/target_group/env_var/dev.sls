targetGroups:
  - name: LaoMao-dev-NEWTargetGroup
    port: 443
    region: us-east-1
    protocol: HTTPS
    unhealthyThresholdCount: 2
    healthyThresholdCount: 2
    timeout: 5
    interval: 10 
    healthCheckPath: /policy-engine.css
    vpc: vpc-123456789
    tags:
      - {"Key":"Name", "Value": "LaoMao-dev-NEWTargetGroup"} 
      - {"Key": "Environment", "Value": "dev"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}

  - name: LaoMao-dev-flask-targetgroup
    port: 5000
    region: us-east-1
    protocol: HTTP
    unhealthyThresholdCount: 2
    healthyThresholdCount: 2
    timeout: 5
    interval: 10 
    healthCheckPath: /health
    vpc: vpc-12345679
    tags:
      - {"Key":"Name", "Value": "LaoMao-dev-flask-targetgroup"} 
      - {"Key": "Environment", "Value": "dev"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}