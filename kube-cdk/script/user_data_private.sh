#! /bin/bash
echo Entering user_data_private.sh, stackId=${AWS::StackId}, stackName=${AWS::StackName}, region=${AWS::Region}

yum-config-manager --enable epel
yum -y update
aws configure set region ${AWS::Region} 
runuser -l ec2-user -c 'aws configure set region ${AWS::Region}'
/opt/aws/bin/ec2-metadata -a
echo leaving user_data_private.sh
