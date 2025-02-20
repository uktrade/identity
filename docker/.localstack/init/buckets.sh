#!/bin/bash
set -x

# Create the S3 bucket
awslocal s3 mb s3://identity.local
echo "identity.local S3 bucket created"

# Create "old" files for testing purposes
cp /fixtures/staff_sso.jsonl /fixtures/staff_sso_2.jsonl
touch -d "$(date -R -r /fixtures/staff_sso.jsonl) - 1 day" /fixtures/staff_sso_2.jsonl
cp /fixtures/staff_sso.jsonl /fixtures/staff_sso_3.jsonl
touch -d "$(date -R -r /fixtures/staff_sso.jsonl) - 1 month" /fixtures/staff_sso_3.jsonl

# Add files to the bucket
awslocal s3 cp /fixtures/staff_sso.jsonl s3://identity.local/data-flow/exports/local-development/StaffSSOUsersPipeline/20241106T000000/full_ingestion.jsonl
awslocal s3 cp /fixtures/staff_sso_2.jsonl s3://identity.local/data-flow/exports/local-development/StaffSSOUsersPipeline/20241105T000000/full_ingestion.jsonl
awslocal s3 cp /fixtures/staff_sso_3.jsonl s3://identity.local/data-flow/exports/local-development/StaffSSOUsersPipeline/20241006T000000/full_ingestion.jsonl
echo "Staff SSO file added to bucket"

set +x
echo "S3 Configured"
