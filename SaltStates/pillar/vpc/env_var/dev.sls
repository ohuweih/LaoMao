vpcs:
  - name: salt-test-vpc
    cidr: "172.20.1.0/26"
    dnsHostNames: True
    routeTables:
      - name: salt-test-vpc-app_route-123
        cidr: "0.0.0.0/0"
        region: us-east-1
        vpcName: salt-test-vpc
        tags: {"Name": "salt-test-vpc-app_route-123", "vpc": "vpc-0ab445d0a2c633df4", "ManagedBy": "Salt", "Project": "LaoMao", "DELETETHIS": "True"}
      - name: salt-test-vpc-db_route-123
        cidr: "0.0.0.0/0"
        region: us-east-1
        vpcName: salt-test-vpc
        tags: {"Name": "salt-test-vpc-db_route-123", "vpc": "vpc-0ab445d0a2c633df4", "ManagedBy": "Salt", "Project": "LaoMao", "DELETETHIS": "True"}
    region: us-east-1
    tags: {"Name": "salt-test-vpc", "ManagedBy": "Salt", "Project": "LaoMao", "DELETETHIS": "True"} 
    subnets:
      - name: salt-test-subnet
        cidr: "172.20.1.0/26"
        az: us-east-1a
        routeTableName: "salt-test-vpc-app_route"
        tags: {"Name": "salt-test-subnet", "ManagedBy": "Salt", "Project": "LaoMao", "DELETETHIS": "True"}