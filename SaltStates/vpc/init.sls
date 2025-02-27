{% set state_id_prefix  = "vpc" %}

{% if pillar['vpcs'] is defined %}
{% set vpcs = pillar['vpcs'] %}
{% for vpc in vpcs %} 


{{state_id_prefix}}_create_vpc_{{vpc.name}}:
  boto_vpc.present:
    - name: {{ vpc.name }}
    - cidr_block: {{ vpc.cidr }}
    - dns_hostnames: {{ vpc.dnsHostNames }}
    - region: {{ vpc.region }}
    - tags: {{ vpc.tags | tojson }}


{% if vpc.internetGatewayName is defined %}
{{state_id_prefix}}_create_internet_gateway:
  boto_vpc.internet_gateway_present:
    - name: {{ vpc.internetGatewayName }}
    - vpc_name: {{vpc.name}}
    - region: {{ vpc.region }}
    - tags: {{ tag | tojson }}
{% endif %}


{% for routeTable in vpc.routeTables %}
{{ state_id_prefix }}_create_route_table_{{routeTable.name}}:
  boto_vpc.route_table_present:
    - name: {{ routeTable.name }}
    - region: {{ routeTable.region }}
    - vpc_name: {{ vpc.name}}
    - routes:
      - destination_cidr_block: {{ vpc.cidr }}
        instance_id: i-019c81757bfa53681
    - tags: {{ routeTable.tags | tojson}}
{% endfor %}


{% for subnet in vpc.subnets %}
{{ state_id_prefix }}_create_vpc_{{vpc.name}}_{{subnet.name}}:
  boto_vpc.subnet_present:
    - name: {{ subnet.name }}
    - vpc_name: {{ vpc.name }}
    - cidr_block: {{ subnet.cidr }}
    - region: {{ vpc.region }}
    - availability_zone: {{ subnet.az }}
    - tags: {{ subnet.tags | tojson }}


{% if subnet.natGateway is defined and subnet.natGateway == True %}
boto_vpc.nat_gateway_present:
  - subnet_name: {{ subnet.name }}
{% endif %}
{% endfor %}

{% endfor %}
{% endif %}


### find a way to add Transit gateway here. Might need to be a custom module. ###