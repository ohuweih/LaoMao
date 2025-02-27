{% set state_id_prefix = "db_schema" %}

{{ state_id_prefix }}_create_schema:
  cmd.run:
    - runas: oracle
    - cwd: /u01/app/oracle/product/19.3.0/dbhome_1/bin/
    - env:
      - ORACLE_SID: oracle
      - ORACLE_HOME: /u01/app/oracle/product/19.3.0/dbhome_1/
      - PATH: $ORACLE_HOME/bin:$PATH
      - ORACLE_BASE: /tmp
    - name: echo 'CREATE USER {{ pillar['db_schema'] }} IDENTIFIED BY {{ pillar['schema_password'] }} DEFAULT TABLESPACE users TEMPORARY TABLESPACE temp QUOTA UNLIMITED ON users;' | ./sqlplus / as sysdba 
    - unless: echo "SELECT username FROM dba_users WHERE username = {{ pillar['db_schema'] }};" | ./sqlplus / as sysdba | grep {{ pillar['db_schema'] }}


{{state_id_prefix}}_grant_privileges_schema: 
  cmd.run: 
    - runas: oracle
    - cwd: /u01/app/oracle/product/19.3.0/dbhome_1/bin/
    - env:
      - ORACLE_SID: oracle
      - ORACLE_HOME: /u01/app/oracle/product/19.3.0/dbhome_1/
      - PATH: $ORACLE_HOME/bin:$PATH
      - ORACLE_BASE: /tmp
    - name: echo 'GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE TRIGGER, CREATE SEQUENCE, CREATE PROCEDURE TO {{ pillar['db_schema'] }};' | ./sqlplus as sysdba 
    - require: 
      - cmd: {{ state_id_prefix }}_create_schema