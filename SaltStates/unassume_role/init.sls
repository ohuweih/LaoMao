unassume_boto_role:
  cmd.run:
    - name: rm -rf ~/.boto

unassume_boto3_role:
  cmd.run:
    - name: rm -rf ~/.aws/credentials