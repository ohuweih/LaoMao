{% set env = salt['grains.get']('env') %}
include:
  - lambda.env_var.{{ env }}