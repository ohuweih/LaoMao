{% set env = salt['grains.get']('env') %}
include:
  - assume_role.env_var.{{ env }}