ecsClusters:
  - clusterName: NAME-ecs-cluster
    clusterTags: {"Name": "NAME-ecs-cluster", "Environment": "dev", "Manageby": "Salt"}
    ecsTasks:

      - taskDefinition: NAME-ui
        taskTags: {"Name": "NAME-ui", "Environment": "dev", "Manageby": "Salt"}
        serviceName: flask
        containerPort: 443
        hostPort: 443
        image: 'Image Link'
        logGroup: NAME-ecs-ui
        taskRole: "arn:aws:iam::123456789123:role/RoleNAme"
        executionRole: "arn:aws:iam::123456789123:role/RoleNAme"
        envVar: 
          - {"name": "hostname","value": "127.0.0.1"}
          - {"name": "service","value": "nignx"}
        credentialsParameter: arn:aws:secretsmanager:us-east-1:123456789123:secret:SecretName

    ecsServices:
      - serviceName: frontend
        taskDefinition: NAME-taskDefinition-combined-ALB:9
        clusterName: NAME-ecs-cluster
        targetGroup: NAME-NEWTargetGroup
        containerPort: 443
        minContainers: 1
        maxContainers: 3
        desiredCount: 1
        ecsServiceTags: {"Name": "NAME", "Environment": "dev", "Manageby": "Salt"}
        subnets:
          - subnet-123456789
          - subnet-123456789
        containerSecGrp:
          - sg-123456798