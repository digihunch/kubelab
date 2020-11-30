#! /bin/bash
# When this script is used by (e.g. Python) script driven by AWS cdk, intrinsic function core.Fn.sub needs to process this file to replace pseudo parameters with actual values. Therefore this script cannot run as a bash script due to the presence of pseudo parameters, nor should it include any pattern that misleads core.Fn.sub with patterns that appears to be a pseudo parameter, even in comments
 
echo Entering user data script, stackId=${AWS::StackId}, stackName=${AWS::StackName}, region=${AWS::Region}
yum-config-manager --enable epel
yum -y update    # including aws-cfn-bootstrap
yum -y install jq
#amazon-linux-extras install -y ansible2 python3.8
#ln -s python3.8 /usr/bin/python3
aws configure set region ${AWS::Region}
MyInstID=`curl -s http://169.254.169.254/latest/meta-data/instance-id`; ResourceLogicalID=`aws ec2 describe-instances --instance-ids $MyInstID | jq -r ".Reservations[].Instances[].Tags[] | select(.Key==\"aws:cloudformation:logical-id\") |.Value"`
#/opt/aws/bin/cfn-init -v --stack ${AWS::StackName} --resource $ResourceLogicalID --configsets bastion_host_cs
runuser -l ec2-user -c 'aws configure set region ${AWS::Region}; echo -n MyInstID='$MyInstID';echo and ResourceLogicalID='$ResourceLogicalID
runuser -l ec2-user -c 'KeyPairName='$MyInstID'-pubkey;echo Creating KeyPair $KeyPairName;aws ec2 create-key-pair --key-name $KeyPairName | jq -r ".KeyMaterial" > ~/.ssh/id_rsa;chmod 400 ~/.ssh/id_rsa'
#/opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource $ResourceLogicalID
echo Leaving user data script

