{% set env = "dev" %}
{% set ip_address = salt['grains.get']('ipv4')[0] %}
{% set region = 'us-east-1' %}
{% set id = grains['id'] %}
{% set instance_id = salt['ec2_utils.get_instance_id_by_ip'](ip_address, region) %}
{% set tags = {
    'HostName': id,
    'Environment': env,
    'OS': 'RHEL8.9',
    'PatchGroup': 'RHEL',
    'Project': 'gaies-pe',
    'ManagedBy': 'Salt'
} %}



{% set state_id_prefix = "add_ec2_resource" %}


{{ state_id_prefix}}_sgs_to_instance:
  module.run:
    - name: ec2_utils.modify_instance_sg
    - region: {{ region }}
    - instance_id: {{ instance_id }}
    - security_group_names: {{ pillar['security_group_names'] }}


{{ state_id_prefix }}_tag_instance:
  module.run:
    - name: ec2_utils.tag_instance
    - region: {{ region }}
    - instance_id: {{ instance_id }}
    - tags: {{ tags | tojson }}