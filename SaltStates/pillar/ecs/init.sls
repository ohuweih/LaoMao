{% set env = salt['grains.get']('env') %}
include:
  - ecs.env_var.{{ env }}