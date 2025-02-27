import boto3

def create_tg(tgname, protocol, port, vpc_id, health_check_path, health_check_interval_seconds, health_check_timeout_seconds, healthy_threshold_count, unhealthy_threshold_count, tags):
    client = boto3.client('elbv2', region_name='us-east-1')
    try:
        tg = client.describe_target_groups(
            Names=[tgname]
        )
        if tg['TargetGroups'][0]['TargetGroupArn']:
            __salt__['grains.set'](tgname, tg['TargetGroups'][0]['TargetGroupArn'])
            print(f"Target group {tgname} exists")
            print(f"Checking if {tgname} is up to date with pillars")
            if tg['TargetGroups'][0]['HealthCheckIntervalSeconds'] != health_check_interval_seconds:
                print(f"Updating {tgname} to match pillars")
                response = client.modify_target_group(
                    TargetGroupArn=tg['TargetGroups'][0]['TargetGroupArn'],
                    HealthCheckEnabled=True,
                    HealthCheckPath=health_check_path,
                    HealthCheckIntervalSeconds=health_check_interval_seconds,
                    HealthCheckTimeoutSeconds=health_check_timeout_seconds,
                    HealthyThresholdCount=healthy_threshold_count,
                    UnhealthyThresholdCount=unhealthy_threshold_count
                )
                return response
    except Exception as e:
        print(e)
        print(f"Target group {tgname} does not exist, Creating")
        response = client.create_target_group(
            Name=tgname,
            Protocol=protocol,
            Port=port,
            VpcId=vpc_id,
            HealthCheckEnabled=True,
            HealthCheckPath=health_check_path,
            HealthCheckIntervalSeconds=health_check_interval_seconds,
            HealthCheckTimeoutSeconds=health_check_timeout_seconds,
            HealthyThresholdCount=healthy_threshold_count,
            UnhealthyThresholdCount=unhealthy_threshold_count,
            TargetType='ip',
            IpAddressType='ipv4',
            Tags=tags
        )
        tgarn = response['TargetGroups'][0]['TargetGroupArn']
        __salt__['grains.set'](tgname, tgarn)
        return response

def create_lb(loadBalancerName, scheme, defaultTargetGroupArn, protocol, port, certificateArn, lbTags, subnets=[], securityGroups=[]):
    lisenerTag = loadBalancerName + "_listern_arn"
    client = boto3.client('elbv2', region_name='us-east-1')
    try:
        lb = client.describe_load_balancers(
            Names=[loadBalancerName]
        )
        if lb['LoadBalancers'][0]['LoadBalancerArn']:
            print(lb['LoadBalancers'][0]['LoadBalancerArn'])
            __salt__['grains.set'](loadBalancerName, lb['LoadBalancers'][0]['LoadBalancerArn'])
            lr = client.describe_listeners(
                LoadBalancerArn=lb['LoadBalancers'][0]['LoadBalancerArn']
                )
            print(lr)
            if lr['Listeners'][0]['ListenerArn']:
                print("listener already created")
                __salt__['grains.set'](lisenerTag, lr['Listeners'][0]['ListenerArn'])
            print(f"Load Balancer {loadBalancerName} exist")
    except Exception as e:
        print(e)
        print(f"Load Balancer {loadBalancerName} does not exist, Creating")
        lb = client.create_load_balancer(
            Name=loadBalancerName,
            Subnets=subnets,
            SecurityGroups=securityGroups,
            Scheme=scheme,
            Type='application',
            IpAddressType='ipv4',
            Tags=lbTags
        )
        lbarn = lb['LoadBalancers'][0]['LoadBalancerArn']
        print("Creating listener for LB")
        listeners = client.create_listener(
            LoadBalancerArn=lbarn,
            Protocol=protocol,
            Port=port,
            Certificates=[
                {
                    'CertificateArn': certificateArn
                }
            ],
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': defaultTargetGroupArn
                }
            ]
        )
        listenerlb = listeners['Listeners'][0]['ListenerArn']
        __salt__['grains.set'](lisenerTag, listenerlb)
        return listenerlb


def create_rule(sticky, targetGroupArn, priority, tags, loadBalancerName, hostHeader=[], method=[]):
    lisenerTag = loadBalancerName + "_listern_arn"
    listenerlb = __salt__['grains.get'](lisenerTag)
    client = boto3.client('elbv2', region_name='us-east-1')
    try:
        rules = client.describe_rules(
            RuleArns=[__salt__['grains.get'](tags[0]['Value'])]
        )
        if rules['Rules'][0]['RuleArn']:
            print(f"Rule {tags[0]['Value']} exists")
    except Exception as e:
        print(e)
        print("Creating Rules")
        if hostHeader != [] and method != []:
            create_rules = client.create_rule(
                    ListenerArn=listenerlb,
                    Tags=tags,
                    Conditions=[
                        {
                            'Field': 'host-header',
                            'HostHeaderConfig': {
                                'Values': hostHeader
                            }
                        },
                        {
                            'Field': 'http-request-method',
                            'HttpRequestMethodConfig': {
                                'Values': method
                            }
                        }
                    ],
                    Actions= [
                        {
                            'ForwardConfig':{
                                'TargetGroupStickinessConfig': {
                                    'DurationSeconds': 3600,
                                    'Enabled': sticky
                                },
                                'TargetGroups': [
                                    {
                                        'TargetGroupArn': targetGroupArn,
                                        'Weight': 1
                                    }
                                ]
                            },
                            'Order': 1,
                            'TargetGroupArn': targetGroupArn,
                            'Type': 'forward'
                        }
                    ],
                Priority=priority
            )
            print(create_rules)
        if hostHeader != [] and method == []:
            create_rules = client.create_rule(
                    ListenerArn=listenerlb,
                    Tags=tags,
                    Conditions=[
                        {
                            'Field': 'host-header',
                            'HostHeaderConfig': {
                                'Values': hostHeader
                            }
                        }
                    ],
                    Actions= [
                        {
                            'ForwardConfig':{
                                'TargetGroupStickinessConfig': {
                                    'DurationSeconds': 3600,
                                    'Enabled': sticky
                                },
                                'TargetGroups': [
                                    {
                                        'TargetGroupArn': targetGroupArn,
                                        'Weight': 1
                                    }
                                ]
                            },
                            'Order': 1,
                            'TargetGroupArn': targetGroupArn,
                            'Type': 'forward'
                        }
                    ],
                Priority=priority
            )
            print(create_rules)
        if hostHeader == [] and method != []:
            create_rules = client.create_rule(
                    ListenerArn=listenerlb,
                    Tags=tags,
                    Conditions=[
                        {
                            'Field': 'http-request-method',
                            'HttpRequestMethodConfig': {
                                'Values': method
                            }
                        }
                    ],
                    Actions= [
                        {
                            'ForwardConfig':{
                                'TargetGroupStickinessConfig': {
                                    'DurationSeconds': 3600,
                                    'Enabled': sticky
                                },
                                'TargetGroups': [
                                    {
                                        'TargetGroupArn': targetGroupArn,
                                        'Weight': 1
                                    }
                                ]
                            },
                            'Order': 1,
                            'TargetGroupArn': targetGroupArn,
                            'Type': 'forward'
                        }
                    ],
                Priority=priority
            )
            print(create_rules)
        return create_rules