#! /bin/bash
echo Entering user_data_public.sh, stackId=${AWS::StackId}, stackName=${AWS::StackName}, region=${AWS::Region}

yum-config-manager --enable epel
yum -y update

runuser -l ec2-user -c 'aws configure set region ${AWS::Region} && \
                        MyInstID=`curl -s http://169.254.169.254/latest/meta-data/instance-id` && \
                        echo InstanceID=$MyInstID'

echo leaving user_data_public.sh