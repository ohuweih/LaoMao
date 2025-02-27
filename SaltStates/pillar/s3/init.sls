{% set env = salt['grains.get']('env') %}
include:
  - s3.env_var.{{ env }}