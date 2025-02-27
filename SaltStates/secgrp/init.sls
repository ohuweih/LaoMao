{% set state_id_prefix = "secgrp" %}

{% if pillar['secgrps'] is defined %}
{% set secgrps = pillar['secgrps'] %}
{% for secgrp in secgrps %}


{{ state_id_prefix }}_create_{{ secgrp.name }}:
  boto_secgroup.present:
    - name: {{ secgrp.name }}
    - description: {{ secgrp.description }}
    - vpc_id: {{ secgrp.vpc }}
    - tags: {{ secgrp.tags | tojson }}
    - region: us-east-1


{{ state_id_prefix }}_slow_it_down {{secgrp.name}}:
  cmd.run:
    - name: sleep 2


{{ state_id_prefix }}_set_secgrp_{{ secgrp.name }}:
  boto_secgroup.present:
    - name: {{ secgrp.name }}
    - description: {{ secgrp.description }}
    - vpc_id: {{ secgrp.vpc }}
    {% if secgrp.egressRules is defined %}
    {% for egressRule in secgrp.egressRules %}
    - rules_egress:
      - ip_protocol: {{ egressRule.ipProtocol }}
        from_port: {{ egressRule.fromPort }}
        to_port: {{ egressRule.toPort }}
        cidr_ip: {{ egressRule.cidrIp }}
    {% endfor %}
    {% endif %}
    - rules:
      {% for rule in secgrp.rules %}
      - ip_protocol: {{ rule.ipProtocol }}
        from_port: {{ rule.fromPort }}
        to_port: {{ rule.toPort}}
      {% if rule.cidrIp is defined %}
        cidr_ip: {{ rule.cidrIp }}
      {% else %}
        source_group_name: {{ rule.sourceGroupName }}
      {% endif %}
      {% endfor %}
    - tags: {{ secgrp.tags }}
    - region: us-east-1


{{ state_id_prefix }}_slow_it_down_again_{{secgrp.name}}:
  cmd.run:
    - name: sleep 2

{{ state_id_prefix }}_get_arn_{{ secgrp.name }}:
  grains.present:
    - name: {{ secgrp.name }}
    - value: {{ salt['boto_secgroup.get_group_id'](secgrp.name) }}
    - force: True

{% endfor %}
{% endif %}
