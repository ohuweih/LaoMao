import boto3

def create_lambda(functionName, roleName, image, description, timeout, memory, subnetIds, securityGroupIds, storageSize, ipv6Allowed=False, region="us-east-1"):
    client = boto3.client('lambda', region_name=region)
    try:
        describeLambda = client.get_function(
            FunctionName=functionName
        )
        print(f"function {functionName} already created, Checking if up to date with pillars")
        if describeLambda['Configuration']['Code']['ImageUri'] != image:
            updateLambda = client.update_function_configuration(
            FunctionName=functionName,
            Role=roleName,
            Code={
                'ImageUri': image
            },
            Description=description,
            Timeout=timeout,
            MemorySize=memory,
            VpcConfig={
                'SubnetIds': subnetIds,
                'SecurityGroupIds': securityGroupIds,
                'Ipv6AllowedForDualStack': ipv6Allowed
            },
            PackageType='Image',
            EphemeralStorage={
                'Size': storageSize
            },
            LoggingConfig={
                'LogFormat': 'JSON',
                'ApplicationLogLevel': 'INFO',
                'SystemLogLevel': 'INFO'
            }
        )
        print("updated function")
        return updateLambda
    except Exception as e:
        print(e)
        print(f"Creating lambda {functionName}")
        createLambda = client.create_function(
            FunctionName=functionName,
            Role=roleName,
            Code={
                'ImageUri': image
            },
            Description=description,
            Timeout=timeout,
            MemorySize=memory,
            VpcConfig={
                'SubnetIds': subnetIds,
                'SecurityGroupIds': securityGroupIds,
                'Ipv6AllowedForDualStack': ipv6Allowed
            },
            PackageType='Image',
            EphemeralStorage={
                'Size': storageSize
            },
            LoggingConfig={
                'LogFormat': 'JSON',
                'ApplicationLogLevel': 'INFO',
                'SystemLogLevel': 'INFO'
            }
        )
        print(f"Created function {functionName}")
        return createLambda


def tag_lambda(resource, tags, region="us-east-1"):
    client = boto3.client('lambda', region_name=region)
    if resource:
        response = client.tag_resource(
            Resource = resource,
            Tags = tags
        )
        return response
    else:
        print("Need to pass the Lambda ARN in order to tag it.")
        return None