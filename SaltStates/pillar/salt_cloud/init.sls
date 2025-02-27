{% set env = salt['grains.get']('env') %}
include:
  - salt_cloud.env_var.{{ env }}