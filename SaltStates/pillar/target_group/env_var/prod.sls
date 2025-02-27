targetGroups:
  - name: LaoMao-prod-targetgroup
    port: 443
    region: us-east-1
    protocol: HTTPS
    unhealthyThresholdCount: 2
    healthyThresholdCount: 2
    timeout: 5
    interval: 10 
    healthCheckPath: /policy-engine.css
    vpc: "vpc-1234564897"
    tags:
      - {"Key":"Name", "Value": "LaoMao-prod-ui-targetgroup"} 
      - {"Key": "Environment", "Value": "prod"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}

  - name: LaoMao-prod-flask-targetgroup
    port: 5000
    region: us-east-1
    protocol: HTTP
    unhealthyThresholdCount: 2
    healthyThresholdCount: 2
    timeout: 5
    interval: 10 
    healthCheckPath: /health
    vpc: "vpc-123456798"
    tags:
      - {"Key":"Name", "Value": "LaoMao-prod-flask-targetgroup"} 
      - {"Key": "Environment", "Value": "prod"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}