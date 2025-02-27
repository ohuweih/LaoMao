secgrps:
  - name: LaoMao-dev-common-scg-gitlab-pipeline-deploy
    description: "Common secgrp"
    vpc: vpc-123456789
    rules:
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 1.1.1.1/32
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 2.2.2.2/32
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 10.0.0.1/32
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 10.22.4.3/24
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 3.2.54.4/28
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 10.0.0.5/32
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 10.10.10.10/32
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        cidrIp: 10.2.3.6/16
        description: some description
      - ipProtocol: tcp
        fromPort: 1521
        toPort: 1521
        cidrIp: 1.1.1.1/24
        description: some description
      - ipProtocol: all
        fromPort: -1
        toPort: -1
        sourceGroupName: LaoMao-dev-common-scg-gitlab-pipeline-deploy
    tags: {"Name": "LaoMao-dev-common-scg-gitlab-pipeline-deploy", "vpc": "vpc-1234567489", "ManagedBy": "Salt", "Project": "LaoMao", "DELETETHIS": "True"}