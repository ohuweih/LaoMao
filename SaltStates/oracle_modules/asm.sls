{% set state_id_prefix = "oracle.asm" %}

{% if grains['grid_installed'] is defined %}
{{ state_id_prefix }}_already_installed:
  cmd.run:
    - name: echo grid is already installed
{% else %} 

{#
{{ state_id_prefix }}_umount_disk:
  mount.unmounted:
    - name: /data
    - device: {{ pillar['asm_device'] }}


{{ state_id_prefix }}_create_partition_label:
  module.run:
    - name: partition.mklabel
    - device: {{ pillar['asm_device'] }}
    - label_type: gpt


{{ state_id_prefix }}_oracleasm_1st_partition:
  module.run:
    - name: partition.mkpart
    - device: {{ pillar['asm_device'] }}
    - part_type: primary
    - start: 0%
    - end: 50%
    - fs_type: ''
    - part_num: 1


{{ state_id_prefix }}_oracleasm_2st_partition:
  module.run:
    - name: partition.mkpart
    - device: {{ pillar['asm_device'] }}
    - part_type: primary
    - start: 50%
    - end: 100%
    - fs_type: ''
    - part_num: 2
#}

{{ state_id_prefix }}_oracleasm_configure_init:
  cmd.run:
    - name: /usr/sbin/oracleasm init


{{ state_id_prefix }}_oracleasm_configure_commmand:
  cmd.run:
    - name: oracleasm configure -u {{ pillar["oracle_grid_user"] }} -g {{ pillar["oracle_group"] }} -s y -e


{{ state_id_prefix }}_oracleasm_service:
  service.running:
    - name: oracleasm
    - enable: True
    - reload: True


{{ state_id_prefix }}_oracleasm_createp1disk_command:
  cmd.run:
    - name: oracleasm createdisk DATA1 {{ pillar['asm_device'] }}p1


{{ state_id_prefix }}_oracleasm_createp2disk_command:
  cmd.run:
    - name: oracleasm createdisk DATA2 {{ pillar['asm_device'] }}p2

{{ state_id_prefix }}_add_sleep:
  cmd.run:
    - name: sleep 10

{{ state_id_prefix }}_oracleasm_scandisks_command:
  cmd.run:
    - name: oracleasm scandisks


{{ state_id_prefix }}_change_disk_perms:
  file.managed:
    - name: {{ pillar['asm_device'] }}
    - user: grid
    - group: oinstall
    - replace: False


{{ state_id_prefix }}_change_part1_perms:
  file.managed:
    - name: {{ pillar['asm_device'] }}p1
    - user: grid
    - group: oinstall
    - replace: False


{{ state_id_prefix }}_change_part2_perms:
  file.managed:
    - name: {{ pillar['asm_device'] }}p2
    - user: grid
    - group: oinstall
    - replace: False

{% endif %}