{% set state_id_prefix = "target_group" %}


{% if pillar['targetGroups'] is defined %}
{% set targetGroups = pillar['targetGroups'] %}
{% for targetGroup in targetGroups %} 


### Create target group for LB ###
{{ state_id_prefix }}_create_target_group_{{ targetGroup.name }}:
  module.run:
    - name: load_balancer_utils.create_tg
    - tgname: {{ targetGroup.name }}
    - port: {{ targetGroup.port }}
    - protocol: {{ targetGroup.protocol }}
    - unhealthy_threshold_count: {{ targetGroup.unhealthyThresholdCount }}
    - healthy_threshold_count: {{ targetGroup.healthyThresholdCount }}
    - health_check_timeout_seconds: {{ targetGroup.timeout }}
    - health_check_interval_seconds: {{ targetGroup.interval }}
    - health_check_path: {{ targetGroup.healthCheckPath }}
    - vpc_id: {{ targetGroup.vpc }}
    - tags: {{ targetGroup.tags }}

{% endfor %}
{% endif %}