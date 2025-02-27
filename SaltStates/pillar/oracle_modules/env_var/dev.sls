#!yaml|gpg

### This is used in oracle_modules.common ###
oracle_users:
  oracle:
    name: oracle
    uid: 502
    gid: 501
  grid:
    name: grid
    uid: 511
    gid: 501
oracle_groups:
  oinstall:
    name: oinstall
    gid: 501
  dba:
    name: dba
    gid: 502
  dgdba:
    name: dgdba
    gid: 503
  oper:
    name: oper
    gid: 504
  asmadmin:
    name: asmadmin
    gid: 505
  asmdba:
    name: asmdba
    gid: 506
  asmoper:
    name: asmoper
    gid: 507
  backupdba:
    name: backupdba
    gid: 508
  kmdba:
    name: kmdba
    gid: 509
  racdba:
    name: racdba
    gid: 510

### This is used in asm ###
asm_device: /dev/nvme1n1

### this is used by asm and grid
oracle_grid_user: grid
oracle_grid_version: 19.3.0
oracle_grid_version_long: 193000
oracle_grid_inventory_dir: /u01/app/oracle/product/grid_oraInventory
oracle_asm_sys_password: Hello123! ### This should be constructed by the salt master and passed in ###


### this is used by DB ###
oracle_db_inventory_dir: /u01/app/oracle/product/db_oraInventory
oracle_db_version: 19.3.0
oracle_db_version_long: 193000
starter_db_password: Hello123! ### This should be constructed by the salt master and passed in ###


### this is used my fusion ###
middleware_version: "12.2.1.4.0"
middleware_inventory_dir: /u01/app/oracle/product/middleware_oraInventory
middleware_oracle_home: /u01/app/oracle/product/12.2.1.4.0/middleware
fusion_zip_files:
  - "V983368-01.zip"
  - "V983357-01.zip"


### this is used by all oracle states ###
oracle_group: oinstall
oracle_user: oracle
app_service_account_id: user
app_service_account_group: group
oracle_asm_monitor_password: Hello123! ### This should be constructed by the salt master and passed in ###