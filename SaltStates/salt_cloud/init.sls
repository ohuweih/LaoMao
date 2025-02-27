{% set state_id_prefix = "salt_cloud" %}

{{ state_id_prefix }}_manage_ec2_profiles:
  file.managed:
    - name: /etc/salt/cloud.profiles.d/ec2_profiles.conf
    - user: root
    - group: root
    - mode: 0644
    - makedirs: True
    - template: jinja
    - source: salt://salt_cloud/files/ec2_profiles.conf


{{ state_id_prefix }}_manage_cloud_ec2_provider:
  file.managed:
    - name: /etc/salt/cloud.providers.d/ec2_providers.conf
    - user: root
    - group: root
    - mode: 0644
    - makedirs: True
    - template: jinja
    - source: salt://salt_cloud/files/ec2_providers.conf