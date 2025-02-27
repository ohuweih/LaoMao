{% set env = salt['grains.get']('env') %}
include:
  - efs.env_var.{{ env }}