{% set state_id_prefix = "ecr" %}

{% if pillar['ecrValues'] is defined %}
{% set ecrValues = pillar['ecrValues'] %}
{% for ecrValue in ecrValues %} 


{{state_id_prefix}}_create_ecr_{{ecrValue.repoName}}:
  module.run:
    - name: ecr_utils.create_ecr
    - repoName: {{ ecrValue.repoName }}

{% endfor %}
{% endif %}