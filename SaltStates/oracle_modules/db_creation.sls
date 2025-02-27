{% set state_id_prefix = 'db_creation' %}


{{ state_id_prefix }}_start_the_db:
  cmd.run:
    - runas: oracle
    - cwd: /u01/app/oracle/product/19.3.0/dbhome_1/bin/
    - env:
      - ORACLE_SID: oracle
      - ORACLE_HOME: /u01/app/oracle/product/19.3.0/dbhome_1/
      - PATH: $ORACLE_HOME/bin:$PATH
      - ORACLE_BASE: /tmp
    - name: echo 'STARTUP NOMOUNT;' | ./sqlplus / as sysdba


{{ state_id_prefix }}_create_the_db:
  cmd.run:
    - runas: oracle
    - cwd: /u01/app/oracle/product/19.3.0/dbhome_1/bin/
    - env:
      - ORACLE_SID: oracle
      - ORACLE_HOME: /u01/app/oracle/product/19.3.0/dbhome_1/
      - PATH: $ORACLE_HOME/bin:$PATH
      - ORACLE_BASE: /tmp
    - name: echo "CREATE DATABASE oracle USER SYS IDENTIFIED BY Passw0rd USER SYSTEM IDENTIFIED BY Passw0rd LOGFILE GROUP 1 '/u01/app/oracle/product/19.3.0/dbhome_1/redo01.log' SIZE 50M, GROUP 2 '/u01/app/oracle/product/19.3.0/dbhome_1/redo02.log' SIZE 50M MAXLOGFILES 5 MAXLOGMEMBERS 5 MAXDATAFILES 100 MAXINSTANCES 1 CHARACTER SET AL32UTF8 NATIONAL CHARACTER SET AL16UTF16 DATAFILE '/u01/app/oracle/product/19.3.0/dbhome_1/system01.bdf' SIZE 500M AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED SYSAUX DATAFILE '/u01/app/oracle/product/19.3.0/dbhome_1/sysaux01.bdf' SIZE 500M AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED DEFAULT TEMPORARY TABLESPACE temp TEMPFILE '/u01/app/oracle/product/19.3.0/dbhome_1/temp01.bdf' SIZE 50M UNDO TABLESPACE undotbs1 DATAFILE '/u01/app/oracle/product/19.3.0/dbhome_1/undotbs01.dbf' SIZE 200M AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;" | ./sqlplus / as sysdba
    - unless: echo 'SELECT name, open_mode FROM v$database' | grep WRITE


{{ state_id_prefix }}_create_user_table:
  cmd.run:
    - runas: oracle
    - cwd: /u01/app/oracle/product/19.3.0/dbhome_1/bin/
    - env:
      - ORACLE_SID: oracle
      - ORACLE_HOME: /u01/app/oracle/product/19.3.0/dbhome_1/
      - PATH: $ORACLE_HOME/bin:$PATH
      - ORACLE_BASE: /tmp
    - name: echo "CREATE TABLESPACE users DATAFILE '/u01/app/oracle/product/19.3.0/dbhome_1/users01.bdf' SIZE 500M AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;" | ./sqlplus / as sysdba


{{ state_id_prefix }}_run_scripts:
  cmd.run:
    - runas: oracle
    - cwd: /u01/app/oracle/product/19.3.0/dbhome_1/bin/
    - env:
      - ORACLE_SID: oracle
      - ORACLE_HOME: /u01/app/oracle/product/19.3.0/dbhome_1/
      - PATH: $ORACLE_HOME/bin:$PATH
      - ORACLE_BASE: /tmp
    - names:
      - echo '@?/rdbms/admin/catalog.sql' | ./sqlplus / as sysdba
      - echo '@?/rdbms/admin/catproc.sql' | ./sqlplus / as sysdba
    - unless: echo 'SELECT object_name, status FROM dba_objects WHERE object_name = 'STANDARD' AND object_type = 'PACKAGE';' | ./sqlplus / as sysdba | grep VALID