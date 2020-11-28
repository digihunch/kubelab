#! /bin/bash
echo entering user data script

yum update -y aws-cfn-bootstrap
yum -y update
yum -y install jq

echo leaving user data script

