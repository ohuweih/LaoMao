{% set env = salt['grains.get']('env') %}
include:
  - ecr.env_var.{{ env }}