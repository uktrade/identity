# CloudFront WAF

## Overview
This project is hosted behind a CloudFront Web Application Firewall (WAF).

## File uploads

This firewall causes some issues with users who are uploading files (eg. photos), this means that we need to bypass the WAF on any URLs that are used for file uploads.

Below is a list of all the known URLs that should be bypassed:

- `profiles/<str:slug>/photo`


This has been implemented by adding a custom WAF rule to the CloudFront distribution. This rule is a regular expression that matches the URLs above and bypasses the WAF for them.