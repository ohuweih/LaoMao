loadBalancers:
  - loadBalancerName: "LaoMao-prod-LoadBalancer"
    securityGroups:
      - {{ salt['grains.get']('LaoMao-prod-ecs-fargate-LoadBalancerSecurityGroup') }}
    subnets:
      - subnet-12345678
      - subnet-123456798
    listeners:
    port: 443
    protocol: HTTPS
    certificateArn: arn:aws:acm:us-east-1:123456798:certificate/Cert
    scheme: internal
    account: 1234564798
    defaultTargetGroup: LaoMao-prod-flask-targetgroup
    listenerTags: 
      - {"Key":"Name", "Value": "LaoMao-prod-LR"} 
      - {"Key": "Environment", "Value": "prod"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}
    loadBalancerTags:
      - {"Key":"Name", "Value": "LaoMao-prod-LB"} 
      - {"Key": "Environment", "Value": "prod"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}
    rules:
      - name: a
        targetGroupName: LaoMao-prod-flask-targetgroup
        method:
          - POST
          - OPTIONS
        sticky: True
        priority: 100
        tags:
          - {"Key": "Name", "Value": "LaoMao-prod-flask-rule"}
        hostHeader:
          - URL
      - name: b
        targetGroupName: LaoMao-prod-targetgroup
        hostHeader:
          - URL
        sticky: False
        priority: 110
        tags:
          - {"Key": "Name", "Value": "LaoMao-prod-ui-rule"}
