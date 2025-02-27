{% set state_id_prefix = "efs" %}

{% if pillar['efsValues'] is defined %}
{% set efsValues = pillar['efsValues'] %}
{% for efsValue in efsValues %} 



{{state_id_prefix}}_create_efs_{{ efsValue.name }}:
  module.run:
    - name: efs_utils.create_efs
    - creationToken: {{ efsValue.name }} 
    - performanceMode: {{ efsValue.performanceMode }}
    - encrypted: {{ efsValue.encrypted }} 
    - backup: {{ efsValue.backup }}
    - tags: {{ efsValue.tags }}

{% if efsValue.subnets is defined %}
{% set subnets = efsValue.subnets %}
{% for subnet in subnets %}
{{state_id_prefix}}_create_mount_{{ subnet.subnetId }}:
  module.run:
    - name: efs_utils.create_efs_mt
    - creationToken: {{ efsValue.name }} 
    - subnetId: {{ subnet.subnetId }}
    - ipAddress: {{subnet.ipAddress }}
    - securityGroups: {{ subnet.secGrps }}
{% endfor %}
{% endif %}

{{state_id_prefix}}_create_access_{{ efsValue.name }}:
  module.run:
    - name: efs_utils.create_efs_access
    - creationToken: {{ efsValue.name }} 
{% endfor %}
{% endif %}