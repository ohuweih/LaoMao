import boto3

def create_efs(creationToken, performanceMode, encrypted, tags, backup):
    client = boto3.client('efs', region_name='us-east-1')
    efs = client.create_file_system(
        CreationToken=creationToken,
        PerformanceMode=performanceMode,
        Encrypted=encrypted,
        Backup=backup,
        Tags=tags
    )
    systemId = efs['FileSystemId']
    print(efs)
    __salt__['grains.set'](creationToken, systemId)

def create_efs_mt(creationToken, subnetId, ipAddress, securityGroups):
    client = boto3.client('efs', region_name='us-east-1')
    systemId = __salt__['grains.get'](creationToken)
    efs_mt = client.create_mount_target(
        FileSystemId=systemId,
        SubnetId=subnetId,
        IpAddress=ipAddress,
        SecurityGroups=securityGroups
    )
    print(efs_mt)

def create_efs_access(creationToken):
    client = boto3.client('efs', region_name='us-east-1')
    systemId = __salt__['grains.get'](creationToken)
    response = client.create_access_point(
        FileSystemId=systemId,
        RootDirectory={
            'Path': '/ssl'
        }
    )
    print(response)