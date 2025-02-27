{% set state_id_prefix = "ecs" %}

{% if pillar['ecsClusters'] is defined %}
{% set ecsClusters = pillar['ecsClusters'] %}
{% set env = salt['grains.get']('env') %}

{% for ecsCluster in ecsClusters %} 
{% if ecsCluster.ecsServices  is defined %}
{% set ecsServices = ecsCluster.ecsServices %}
{% if ecsCluster.ecsTasks  is defined %}
{% set ecsTasks = ecsCluster.ecsTasks %}


### create ECS cluster, task, and service. in that order ###
{{state_id_prefix}}_create_cluster_{{ ecsCluster.clusterName }}:
  module.run:
    - name: ecs_utils.createCluster
    - clusterName: {{ ecsCluster.clusterName }}
    - tags: {{ ecsCluster.clusterTags | tojson }}



{% for ecsTask in ecsTasks %}


{{state_id_prefix}}_create_ecs_log_group_{{ ecsTask.taskDefinition }}:
  module.run:
    - name: cloudwatch_utils.createLogGroup
    - logGroupName: {{ ecsTask.taskDefinition }}_{{ ecsTask.serviceName }}_/ecs/


{{state_id_prefix}}_create_task_def_{{ ecsTask.taskDefinition }}:
  module.run:
    - name: ecs_utils.createTaskDefinition
    - taskDefinition: {{ ecsTask.taskDefinition }}
    - tags: {{ ecsTask.taskTags | tojson }}
    - serviceName: gaies-pe-{{env}}-{{ ecsTask.serviceName }}
    - image: {{ ecsTask.image }}
    - containerPort: {{ ecsTask.containerPort }}
    - logGroup: {{ ecsTask.logGroup }}
    - taskRole: {{ ecsTask.taskRole }}
    - hostPort: {{ ecsTask.hostPort }}
    - envVar: {{ ecsTask.envVar}}
    - executionRole: {{ ecsTask.executionRole }}
    - credentialsParameter: {{ ecsTask.credentialsParameter }}
    {% if ecsTask.mountPoint is defined %}
    - mountPoint: {{ ecsTask.mountPoint }}
    - volume: {{ ecsTask.volume }}
    {% endif %}
{% endfor %}


{% for ecsService in ecsServices %}

{{state_id_prefix}}_create_service_{{ ecsService.serviceName }}:
  module.run:
    - name: ecs_utils.createService
    - serviceName: gaies-pe-{{env}}-{{ ecsService.serviceName }}
    - taskDefinition: {{ ecsService.taskDefinition }}
    - clusterName: {{ ecsService.clusterName }}
    - desiredCount: {{ ecsService.desiredCount }}
    - containerPort: {{ ecsService.containerPort }}
    - targetGroup: {{ salt['grains.get'](ecsService.targetGroup) }}
    - subnets: {{ ecsService.subnets }}
    - tags: {{ ecsService.ecsServiceTags | tojson }}
    - containerSecGrp: {{  ecsService.containerSecGrp }}


{{state_id_prefix}}_create_auto_scaling_{{ ecsService.serviceName }}:
  module.run:
    - name: ec2_utils.createScalingTarget
    - resourceId: service/{{ecsService.clusterName}}/gaies-pe-{{ env }}-{{ ecsService.serviceName }}
    - minContainers: {{ ecsService.minContainers }}
    - maxContainers: {{ ecsService.maxContainers }}


{{state_id_prefix}}_put_auto_scaling_{{ ecsService.serviceName }}:
  module.run:
    - name: ec2_utils.putScalingTarget
    - resourceId: service/{{ecsService.clusterName}}/gaies-pe-{{ env }}-{{ ecsService.serviceName }}
    - policyName: gaies-pe-{{ env }}-{{ ecsService.serviceName }}-asp
{% endfor %}

{% endif %}
{% endif %}
{% endfor %}
{% endif %}