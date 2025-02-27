{% set state_id_prefix = "oracle.db" %}

{{ state_id_prefix }}_db_dir:
  file.directory:
    - name: /u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - mode: 0755
    - makedirs: True


{{ state_id_prefix }}_db_archive_file:
  archive.extracted:
    - unless: ls /u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1/bin
    - name: /u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1
    - source: /data/stage/LINUX.X64_{{ pillar["oracle_db_version_long"] }}_db_home.zip
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - enforce_toplevel: False


### add what type of DB we want to use based of pillar ###
{{ state_id_prefix }}_install_file:
  file.managed:
    - name: /u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1/inventory/response/db_install.rsp
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - mode: 0644
    - template: jinja
    - source: salt://oracle_modules/files/db_install.rsp
    - context:
      oracle_db_inventory_dir: {{ pillar['oracle_db_inventory_dir'] }}
      starter_db_password: {{ pillar['starter_db_password'] }}
      oracle_asm_monitor_password: {{ pillar['oracle_asm_monitor_password'] }}
      oracle_version: {{ pillar['oracle_db_version'] }}


{% if grains['oracledb_installed'] is defined %}
{{ state_id_prefix }}_already_installed:
  cmd.run:
    - name: echo oracle db is already installed
{% else %}


{{ state_id_prefix }}_oracle_install:
  cmd.run:
    - name: "./runInstaller -silent -responseFile ./inventory/response/db_install.rsp"
    - runas: oracle
    - cwd: "/u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1"
    - env:
      - ORACLE_HOME: "/u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1"
      - CV_ASSUME_DISTID: "OL7"


{{ state_id_prefix }}_root_sh:
  cmd.run:
    - name: "/u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1/root.sh"
    - runas: root


{{ state_id_prefix }}_set_success_grain:
  grains.present:
    - name: oracledb_installed
    - value: True
    - onchanges:
      - cmd: {{ state_id_prefix }}_root_sh
{% endif %}


{{ state_id_prefix }}_create_db_file:
  file.managed:
    - name: /u01/app/oracle/product/{{ pillar['oracle_db_version'] }}/dbhome_1/dbs/initoracle.ora
    - source: salt://oracle_modules/files/initoracle.ora
    - template: jinja
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - mode: 0644

{{ state_id_prefix }}_create_db_folders:
  file.directory:
    - names:
      - /tmp/fast_recovery_area
      - /tmp/admin/orcl/adump
    - template: jinja
    - user: {{ pillar['oracle_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - mode: 0755