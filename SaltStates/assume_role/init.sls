assume_role_file:
  file.managed:
    - name: /root/switch.sh
    - source: salt://assume_role/files/switch.sh
    - template: jinja
    - mode: 644

assume_role:
  cmd.run:
    - name: sh /root/switch.sh
