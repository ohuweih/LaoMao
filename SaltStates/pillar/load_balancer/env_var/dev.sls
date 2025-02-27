loadBalancers:
  - loadBalancerName: "NAME--LoadBalancer"
    securityGroups:
      - {{ salt['grains.get']('NAME--LoadBalancerSecurityGroup') }}
    subnets:
      - subnet-123456789
      - subnet-123456789
    listeners:
    port: 443
    protocol: HTTPS
    certificateArn: arn:aws:acm:us-east-1:123456789:certificate/Cert
    scheme: internal
    account: 123456798
    defaultTargetGroup: NAME--flask-targetgroup
    listenerTags: 
      - {"Key":"Name", "Value": "NAME--LR"} 
      - {"Key": "Environment", "Value": "dev"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}
    loadBalancerTags:
      - {"Key":"Name", "Value": "NAME--LB"} 
      - {"Key": "Environment", "Value": "dev"}
      - {"Key": "Manageby", "Value": "Salt"} 
      - {"Key": "Project", "Value": "LaoMao"}
    rules:
      - name: a
        targetGroupName: NAME--flask-ECS
        method:
          - POST
          - OPTIONS
        sticky: True
        priority: 210
        tags:
          - {"Key": "Name", "Value": "NAME--flask-rule"}
        hostHeader:
          - URL
      - name: b
        targetGroupName: NAME--NEWTargetGroup
        hostHeader:
          - URL
        sticky: False
        priority: 220
        tags:
          - {"Key": "Name", "Value": "NAME--ui-rule"}
