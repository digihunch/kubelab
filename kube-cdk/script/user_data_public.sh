#! /bin/bash
echo Entering user_data_public.sh, stackId=${AWS::StackId}, stackName=${AWS::StackName}, region=${AWS::Region}

yum-config-manager --enable epel
yum -y update
aws configure set region ${AWS::Region} 
runuser -l ec2-user -c 'aws configure set region ${AWS::Region}'
MyInstID=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
ASGLOGICALID=`aws ec2 describe-instances --instance-ids $MyInstID --query "Reservations[].Instances[].Tags[?Key=='aws:cloudformation:logical-id'].Value" --output text`
echo InstanceID=$MyInstID and ASGLOGICALID=$ASGLOGICALID

echo leaving user_data_public.sh
