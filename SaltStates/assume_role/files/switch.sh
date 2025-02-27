#!/bin/bash
ROLE_ARN={{ pillar['roleArn'] }}
CREDENTIALS=$(aws sts assume-role --role-arn $ROLE_ARN --role-session-name 'dev-salt')
ACCESS_KEY=$(echo $CREDENTIALS | jq -r '.Credentials''.AccessKeyId')
SECRET_KEY=$(echo $CREDENTIALS | jq -r '.Credentials''.SecretAccessKey')
SESSION_TOKEN=$(echo $CREDENTIALS | jq -r '.Credentials''.SessionToken')

cat > ~/.boto <<EOL
[Credentials]
aws_access_key_id = $ACCESS_KEY
aws_secret_access_key = $SECRET_KEY
aws_security_token = $SESSION_TOKEN

[Boto]
ec2_region_name = us-east-1
EOL

cat > ~/.aws/credentials <<EOL
[default]
aws_access_key_id = $ACCESS_KEY
aws_secret_access_key = $SECRET_KEY
aws_security_token = $SESSION_TOKEN
EOL