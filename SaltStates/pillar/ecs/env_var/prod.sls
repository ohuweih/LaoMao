ecsClusters:
  - clusterName: NAME-cluster
    clusterTags: {"Name": "NAME-cluster", "Environment": "prod", "Manageby": "Salt"}
    ecsTasks:
      - taskDefinition: NAME-flask
        taskTags: {"Name": "NAME-flask", "Environment": "prod", "Manageby": "Salt"}
        serviceName: flask
        containerPort: 5000
        hostPort: 5000
        image: 'registry.gitlab.com/gadhs/ai-policy-engine/gen-ai-policy-engine-backend:latest'
        logGroup: NAME-ecs-flask
        taskRole: "arn:aws:iam::123456789123:role/RoleNAme"
        executionRole: "arn:aws:iam::123456789123:role/RoleNAme"
        envVar: 
          - {"name": "hostname","value": "127.0.0.1"}
          - {"name": "service","value": "nignx"}
        credentialsParameter: arn:aws:secretsmanager:us-east-1:123456789123:secret:SecrectName

      - taskDefinition: NAME-ui
        taskTags: {"Name": "NAME-ui", "Environment": "prod", "Manageby": "Salt"}
        serviceName: ui
        containerPort: 443
        hostPort: 443
        mountPoint:  [{"sourceVolume": "NAME","containerPath": "/etc/ssl","readOnly": true}]
        volume: [{"name": NAME,"efsVolumeConfiguration": {"fileSystemId": {{ salt['grains.get']('NAME') }},"rootDirectory": "/ssl"}}]
        image: Image Link
        logGroup: NAME-ecs-ui
        taskRole: "arn:aws:iam::123456789123:role/RoleNAme"
        executionRole: "arn:aws:iam::123456789123:role/RoleNAme"
        envVar: 
          - {"name": "hostname","value": "127.0.0.1"}
          - {"name": "service","value": "nignx"}
        credentialsParameter: arn:aws:secretsmanager:us-east-1:123456789123:secret:SecrectName

    ecsServices:
      - serviceName: flask
        taskDefinition: NAME-flask:1
        clusterName: NAME-cluster
        targetGroup: NAME-flask-targetgroup
        containerPort: 5000
        minContainers: 2
        maxContainers: 4
        desiredCount: 2
        ecsServiceTags: {"Name": "NAME-ecs-flask", "Environment": "prod", "Manageby": "Salt"}
        subnets:
          - subnet-123456789
          - subnet-123456789
        containerSecGrp:
          - {{ salt['grains.get']('NAME-common-scg') }}

      - serviceName: ui
        taskDefinition: NAME-ui:2
        clusterName: NAME-cluster
        targetGroup: NAME-targetgroup
        containerPort: 443
        minContainers: 2
        maxContainers: 4 
        desiredCount: 4
        ecsServiceTags: {"Name": "NAME-ecs-ui", "Environment": "prod", "Manageby": "Salt"}
        subnets:
          - subnet-1235456789
          - subnet-123456798
        containerSecGrp:
          - {{ salt['grains.get']('NAME-common-scg') }}
