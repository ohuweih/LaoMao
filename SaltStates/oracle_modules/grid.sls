{% set state_id_prefix = "oracle.grid" %}
    
{{ state_id_prefix }}_grid_dir:
  file.directory:
    - name: /u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid
    - user: {{ pillar['oracle_grid_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - mode: 0755
    - makedirs: True


{{ state_id_prefix }}_grid_inv_dir:
  file.directory:
    - name: {{ pillar['oracle_grid_inventory_dir'] }}
    - user: {{ pillar['oracle_grid_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - mode: 0755
    - makedirs: True


{{ state_id_prefix }}_grid_archive_file:
  archive.extracted:
    - unless: ls /u01/app/oracle/product/19.3.0/grid/bin
    - name: /u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid
    - source: /data/stage/LINUX.X64_{{ pillar["oracle_grid_version_long"] }}_grid_home.zip
    - user: {{ pillar['oracle_grid_user'] }}
    - group: {{ pillar['oracle_group'] }}
    - enforce_toplevel: False


{{ state_id_prefix }}_install_file:
  file.managed:
    - name: /u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid/inventory/response/grid_install.rsp
    - user: {{ pillar["oracle_grid_user"] }}
    - group: {{ pillar["oracle_group"] }}
    - mode: 0644
    - template: jinja
    - source: salt://oracle_modules/files/grid.rsp
    - context:
      oracle_grid_inventory_dir: {{ pillar['oracle_grid_inventory_dir'] }}
      oracle_asm_sys_password: {{ pillar['oracle_asm_sys_password'] }}
      oracle_asm_monitor_password: {{ pillar['oracle_asm_monitor_password'] }}


{{ state_id_prefix }}_symlnk_file:
  file.symlink:
    - name: /usr/lib64/libnsl.so.1
    - target: /usr/lib64/libnsl.so.2


{% if grains['grid_installed'] is defined %}
{{ state_id_prefix }}_already_installed:
  cmd.run:
    - name: echo grid is already installed


{% else %}
{{ state_id_prefix }}_gridsetup_install:
  cmd.run:
    - name: "./gridSetup.sh -silent -responseFile ./inventory/response/grid_install.rsp"
    - runas: grid
    - cwd: "/u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid/"
    - env:
      - ORACLE_HOME: "/u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid"
      - CV_ASSUME_DISTID: "OL7"


{{ state_id_prefix }}_root_install:
  cmd.run: ### cmd.script instead of run. ###
    - names: 
      - "{{ pillar['oracle_grid_inventory_dir'] }}/orainstRoot.sh"
      - "/u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid/root.sh"
    - runas: root


{{ state_id_prefix }}_gridSetup_2_install:
  cmd.run:
    - name: "./gridSetup.sh -silent -executeConfigTools -responseFile ./inventory/response/grid_install.rsp"
    - runas: grid
    - cwd: "/u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid/"
    - env:
      - ORACLE_HOME: "/u01/app/oracle/product/{{ pillar['oracle_grid_version'] }}/grid"
      - CV_ASSUME_DISTID: "OL7"


{{ state_id_prefix }}_set_success_grain:
  grains.present:
    - name: grid_installed
    - value: True
    - onchanges:
      - cmd: {{ state_id_prefix }}_gridSetup_2_install
{% endif %}