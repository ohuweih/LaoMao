{% set state_id_prefix = "salt_master" %}

{{state_id_prefix}}_pkg_install:
  pkg.installed:
    - pkgs:
      - salt-master
      - salt-cloud


{{ state_id_prefix }}_manage_conf:
  file.managed:
    - name: /etc/salt/master
    - user: root
    - group: root
    - mode: 0644
    - makedirs: True
    - template: jinja
    - source: salt://salt_master/files/master.conf


{{ state_id_prefix }}_manage_etc_salt_gpgkeys_dir:
  file.directory:
    - name: /etc/salt/gpgkeys
    - user: root
    - group: root
    - mode: 0700


{{ state_id_prefix }}_start_salt_master:
  service.running:
    - name: salt-master
    - enable: True
    - watch:
      - file: /etc/salt/master
