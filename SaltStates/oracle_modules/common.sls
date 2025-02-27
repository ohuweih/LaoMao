{% set state_id_prefix = "oracle.common" %}

{{ state_id_prefix }}_packages:
  pkg.installed:
    - sources:
      - oracleasmlib: /data/stage/oracleasmlib-2.0.17-1.el8.x86_64.rpm
      - oracleasm-support: /data/stage/oracleasm-support-2.1.12-1.el8.x86_64.rpm
      - compat-libstdc++-33: /data/stage/compat-libstdc++-33-3.2.3-72.el7.x86_64.rpm
      - compat-libcap1: /data/stage/compat-libcap1-1.10-7.el7.x86_64.rpm
      - oracle-database-preinstall-19c: /data/stage/oracle-database-preinstall-19c-1.0-1.el7.x86_64.rpm


{{ state_id_prefix }}_more_packages:
  pkg.installed:
    - pkgs:
      - binutils 
      - compat-libcap1 
      - gcc 
      - gcc-c++ 
      - glibc 
      - glibc-devel 
      - ksh 
      - libgcc 
      - libstdc++ 
      - libstdc++-devel 
      - libaio 
      - libaio-devel 
      - make 
      - sysstat
      - java-1.8.0-openjdk


{% for id, config in pillar["oracle_groups"].items() %}
{{ state_id_prefix }}_{{ id }}_group:
  group.present:
    - name: {{ config["name"] }}
    - gid: {{ config["gid"] }}
{% endfor %}


{% for id, config in pillar["oracle_users"].items() %}
{{ state_id_prefix }}_{{ id }}_user:
  user.present:
    - name: {{ config["name"] }}
    - uid: {{ config["uid"] }}
    - gid: {{ config["gid"] }}
    - allow_uid_change: True
    - allow_gid_change: True
    - groups: 
      - oinstall
      - dba 
      - dgdba 
      - oper 
      - asmadmin 
      - asmdba 
      - asmoper 
      - backupdba 
      - kmdba 
      - racdba
    - password: ''
{% endfor %}


{{ state_id_prefix }}_firewalld_service:
  service.dead:
    - name: firewalld
    - enable: False


{{ state_id_prefix }}_selinux_mode:
  selinux.mode:
    - name: permissive


{{ state_id_prefix }}_sysctl_file:
  file.managed:
    - name: /etc/sysctl.d/98-oracle.conf
    - user: root
    - group: root
    - mode: 0644
    - source: salt://oracle_modules/files/98_oracle.j2


{{ state_id_prefix }}_limits_file:
  file.managed:
    - name: /etc/security/limits.d/oracle-database-preinstall-19c.conf
    - user: root
    - group: root
    - mode: 0644
    - source: salt://oracle_modules/files/oracle_database_preinstall.j2


{{ state_id_prefix }}_swap_command:
  cmd.run:
    - unless: grep swapfile /proc/swaps
    - names:
      - fallocate -l 2G /swapfile
      - chmod 0600 /swapfile
      - mkswap /swapfile


{{ state_id_prefix }}_swap_mount:
  mount.swap:
    - name: /swapfile
    - persist: True