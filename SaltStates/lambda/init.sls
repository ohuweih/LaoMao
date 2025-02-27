{% set state_id_prefix = "lambda" %}

{% if pillar['functions'] is defined %}
{% set functions = pillar['functions'] %}
{% for function in functions %}


{% if function.image is defined %}

{{ state_id_prefix }}_create_function_{{ function.functionName }}:
  module.run:
    - name: lambda_utils.create_lambda
    - functionName: {{ function.functionName }}
    - roleName: {{ function.roleArn }}
    - image: {{ function.image }}
    - description: {{ function.description }}
    - timeout: {{ function.timeout }}
    - memory: {{ function.memorySize }}
    - subnetIds: {{ function.subnetIds }}
    - securityGroupIds: {{ function.securityGroupIds }}
    - storageSize: {{ function.storageSize }}
{% endif %} 


{{state_id_prefix}}_tag_function_{{ function.functionName }}:
  module.run:
    - name: lambda_utils.tag_lambda
    - resource: arn:aws:lambda:{{ function.region }}:{{ function.account }}:function:{{ function.functionName }}
    - tags: {{ function.tags | tojson }}


{{ state_id_prefix }}_add_arn_grains_{{ function.functionName }}:
  grains.present:
    - name: {{ function.functionName }}
    - value: arn:aws:lambda:{{ function.region }}:{{ function.account }}:function:{{ function.functionName }}


{{ state_id_prefix }}_add_region_grains_{{ function.functionName }}:
  grains.present:
    - name: {{ function.functionName }}_region
    - value: {{ function.region }}
{% endfor %}
{% endif %}