{% set env = salt['grains.get']('env') %}
include:
  - target_group.env_var.{{ env }}