{% set state_id_prefix = "load_balancer" %}


{% if pillar['loadBalancers'] is defined %}
{% set loadBalancers = pillar['loadBalancers'] %}
{% for loadBalancer in loadBalancers %} 


{{ state_id_prefix }}_create_lb_{{ loadBalancer.loadBalancerName }}:
  module.run:
    - name: load_balancer_utils.create_lb
    - loadBalancerName: {{ loadBalancer.loadBalancerName }}
    - scheme: {{loadBalancer.scheme}}
    - subnets: {{ loadBalancer.subnets }}
    - securityGroups: {{ loadBalancer.securityGroups }}
    - defaultTargetGroupArn: {{ salt['grains.get'](loadBalancer.defaultTargetGroup) }}
    - protocol: {{ loadBalancer.protocol }}
    - port: {{ loadBalancer.port }}
    - certificateArn: {{ loadBalancer.certificateArn }}
    - lbTags: {{ loadBalancer.loadBalancerTags }}
    - lrTags: {{ loadBalancer.listenerTags }}


{% for rule in loadBalancer.rules %}
{{ state_id_prefix }}_create_lb_rule_{{ rule.name }}:
  module.run:
    - name: load_balancer_utils.create_rule
    - priority: {{ rule.priority }}
    - loadBalancerName: {{ loadBalancer.loadBalancerName }}
    - sticky: {{rule.sticky}}
    - tags: {{ rule.tags }}
    {% if rule.hostHeader is defined and rule.method is defined %}
    - hostHeader: {{ rule.hostHeader }}
    - method: {{ rule.method }}
    {% elif rule.hostHeader is defined %}
    - hostHeader: {{ rule.hostHeader }}
    {% else %}
    - method: {{ rule.method }}
    {% endif %}
    - targetGroupArn: {{ salt['grains.get'](rule.targetGroupName) }}
    - tags: {{ rule.tags }}
{% endfor %}
{% endfor %}
{% endif %}
