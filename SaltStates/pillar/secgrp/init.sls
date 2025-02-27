{% set env = salt['grains.get']('env') %}
include:
  - secgrp.env_var.{{ env }}