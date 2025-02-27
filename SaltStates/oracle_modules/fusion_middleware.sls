{% set state_id_prefix = "fusion_middleware" %}

{#
{{ state_id_prefix }}_extract_java_file:
  archive.extracted:
    - name: /data/stage/jdk
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - source: /data/stage/openjdk-8u43-linux-x64.tar.gz
    - if_missing: /data/stage/jdk/bin/java


#### i dont think we need to manage the bashrc. We can use env in the salt state when needed ###
{{ state_id_prefix }}_manage_bashrc:
  file.managed:
    - name: /home/{{ pillar['oracle_user'] }}/.bash_profile
    - group: {{ pillar['oracle_group'] }}
    - user: {{ pillar['oracle_user'] }}
    - mode: 600
    - makedir: True
    - source: salt://opa/files/bash_profile.j2
#}


{{ state_id_prefix }}_manage_oracle_home_directory:
  file.directory:
    - name: /u01/app/oracle/product/{{ pillar['middleware_version'] }}
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - mode: 0755
    - makedirs: True


{% for file in pillar['fusion_zip_files'] %}
{{ state_id_prefix }}_extract_fusion_file_{{ file }}:
  archive.extracted:
    - name: /u01/app/oracle/product/{{ pillar['middleware_version'] }}/
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - source: /data/stage/{{ file }}
    - enforce_toplevel: False
    - if_missing: /u01/app/oracle/product/{{ pillar['middleware_version'] }}/fmw_12.2.1.4.0_infrastructure.jar
{% endfor %}

{{ state_id_prefix }}_manage_response_file:
  file.managed:
    - name: /u01/app/oracle/product/{{ pillar['middleware_version'] }}/fmw_responsefile.rsp
    - mode: 0644
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - template: jinja
    - source: salt://oracle_modules/files/fmw_responsefile.j2


{% set grain_middleware_version = salt['grains.get']('middleware_version', 'default_value') %}
{% set map_middleware_version = pillar['middleware_version'] %}
{% if map_middleware_version != grain_middleware_version %}
{{state_id_prefix }}_install_fusion_middleware:
  cmd.run:
    - name: /data/stage/jdk/bin/java -jar fmw_{{ pillar['middleware_version'] }}_infrastructure.jar -silent -responseFile /u01/app/oracle/product/{{ pillar['middleware_version'] }}/fmw_responsefile.rsp
    - runas: oracle
    - cwd: /u01/app/oracle/product/{{ pillar['middleware_version'] }}/

{{ state_id_prefix }}_set_fusion_middleware_version:
  grains.present:
    - name: fusion_middleware_version
    - value: {{ pillar['middleware_version'] }}
    - onchanges:
      - cmd: {{ state_id_prefix }}_install_fusion_middleware
{% endif %}