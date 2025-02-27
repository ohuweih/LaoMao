import boto3


def get_instance_id_by_ip(ip_address, region='us-east-1'):
    """
    Get the instance ID based on the private IP address.
    """
    ec2 = boto3.client('ec2', region_name=region)
    print(ip_address)
    response = ec2.describe_instances(Filters=[{'Name': 'private-ip-address', 'Values':[ip_address]}])
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            return instance['InstanceId']
    return None


def get_security_group_ids_by_names(group_names, region='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': group_names}])
    security_group_ids = [group['GroupId'] for group in response['SecurityGroups']]
    return security_group_ids


def modify_instance_sg(instance_id, security_group_names, region='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region)
    print(f"Modifying instance {instance_id} in region {region} with security groups {security_group_names}")    
    # Get the current security groups of the instance
    response = ec2.describe_instances(InstanceIds=[instance_id])
    current_sg_ids = response['Reservations'][0]['Instances'][0]['SecurityGroups']
    current_sg_ids = [sg['GroupId'] for sg in current_sg_ids]

    # Convert security group names to IDs
    new_sg_ids = get_security_group_ids_by_names(region, security_group_names)
    
    # Combine current and new security group IDs, avoiding duplicates
    all_sg_ids = list(set(current_sg_ids + new_sg_ids))
    
    # Modify the instance to include all security groups
    response = ec2.modify_instance_attribute(
        InstanceId=instance_id,
        Groups=all_sg_ids
    )
    return response


def tag_instance(instance_id, tags, region='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region)
    tag_list =[]
    for key, value in tags.items():
        tag_list.append({'Key': key, 'Value': value})
    print(f"printing tag_list {tag_list}")
    response = ec2.create_tags(Resources=[instance_id], Tags=tag_list)
    return response


def createScalingTarget(resourceId, minContainers, maxContainers, region='us-east-1'):
    client = boto3.client('application-autoscaling', region_name=region)
    response = client.register_scalable_target(
        ServiceNamespace= "ecs",
        ResourceId=resourceId,
        MinCapacity=minContainers,
        MaxCapacity=maxContainers,
        ScalableDimension="ecs:service:DesiredCount"
    )


def createScalingPolicy(policyName, resourceId, autoScalingTargetValue, region='us-east-1'):
    client = boto3.client('application-autoscaling', region_name=region)
    response = client.put_scaling_policy(
        PolicyName=policyName,
        PolicyType="TargetTrackingScaling",
        ResourceId=resourceId,
        TargetTrackingScalingPolicyConfiguration= {
            "PredefinedMetricSpecification" : {
                "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
            },
            "ScaleOutCooldown": 10,
            "ScaleInCooldown": 10,
            "TargetValue": autoScalingTargetValue
        }
    )


def putScalingTarget(resourceId, policyName):
    client = boto3.client('application-autoscaling', region_name='us-east-1')
    response = client.put_scaling_policy(
        PolicyName=policyName,
        ServiceNamespace='ecs',
        ResourceId=resourceId,
        ScalableDimension='ecs:service:DesiredCount',
        PolicyType='TargetTrackingScaling',
        TargetTrackingScalingPolicyConfiguration={
            'TargetValue': 80,
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ECSServiceAverageCPUUtilization'
                }
        }
    )
