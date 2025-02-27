{% set env = salt['grains.get']('env') %}
include:
  - load_balancer.env_var.{{ env }}