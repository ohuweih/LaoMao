{% set state_id_prefix = 's3' %}
{% set env = salt['grains.get']('env') %}

{{state_id_prefix}}_create_bucket_gaies-pe-s3-access-logs-salt:
  module.run:
    - boto_s3_bucket.create:
      - Bucket: gaies-pe-{{ env }}-s3-access-logs


{{state_id_prefix}}_tag_bucket_gaies-pe-s3-access-logs-salt:
  module.run:
    - boto_s3_bucket.put_tagging:
      - Bucket: gaies-pe-{{ env }}-s3-access-logs
      - Key: Project
      - Value: gaies-pe


{% if pillar['s3Buckets'] is defined %}
{% set s3Buckets = pillar['s3Buckets'] %}
{% for s3Bucket in s3Buckets %}


{{state_id_prefix}}_create_bucket_{{ s3Bucket.name }}:
  module.run:
    - boto_s3_bucket.create:
      - Bucket: {{ s3Bucket.name }}


{{state_id_prefix}}_tag_bucket_{{ s3Bucket.name }}:
  module.run:
    - boto_s3_bucket.put_tagging:
      - Bucket: {{ s3Bucket.name }}
      - Key: Project
      - Value: gaies-pe


{{state_id_prefix}}_logging_bucket_{{ s3Bucket.name }}:
  module.run:
    - boto_s3_bucket.put_logging:
      - Bucket: {{ s3Bucket.name }}
      - TargetBucket: {{ s3Bucket.loggingBucket }}
      - TargetPrefix: {{ s3Bucket.name }}


{{state_id_prefix}}_version_bucket_{{ s3Bucket.name }}:
  module.run:
    - boto_s3_bucket.put_versioning:
      - Bucket: {{ s3Bucket.name }}
      - Status: Enabled


{{ state_id_prefix }}_add_lambda_perms{{ s3Bucket.name }}:
  cmd.run:
    - name: aws lambda add-permission --function-name {{ s3Bucket.functionName }} --statement-id s3-event-permission --action lambda:InvokeFunction --principal s3.amazonaws.com --source-arn arn:aws:s3:::{{ s3Bucket.name }}


{{state_id_prefix}}_notification_bucket_{{ s3Bucket.name }}:
  cmd.run:
    - name: "aws s3api put-bucket-notification-configuration --bucket {{ s3Bucket.name }} --notification-configuration '{\"LambdaFunctionConfigurations\": [{\"Id\": \"NewObjectCreated\",\"LambdaFunctionArn\": \"{{ s3Bucket.roleArn }}\",\"Events\": [\"s3:ObjectCreated:*\"]}]}' --region us-east-1"


{% endfor %}
{% endif %}