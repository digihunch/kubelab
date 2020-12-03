#! /bin/bash
# When this script is used by (e.g. Python) script driven by AWS cdk, intrinsic function core.Fn.sub needs to process this file to replace pseudo parameters with actual values. Therefore this script cannot run as a bash script due to the presence of pseudo parameters, nor should it include any pattern that misleads core.Fn.sub with patterns that appears to be a pseudo parameter, even in comments
# There is no need to use cfn-init script to activate config set in this script. It is implicitly done via ApplyCloudFormationInitOptions method
 
echo Entering user_data_bastion.sh, stackId=${AWS::StackId}, stackName=${AWS::StackName}, region=${AWS::Region}
yum-config-manager --enable epel
yum -y update
aws configure set region ${AWS::Region} 
runuser -l ec2-user -c 'aws configure set region ${AWS::Region} && \
                        MyInstID=`curl -s http://169.254.169.254/latest/meta-data/instance-id` && \
                        KeyPairName=$MyInstID-pubkey && \
                        echo Creating KeyPair $KeyPairName && \
                        aws ec2 create-key-pair --key-name $KeyPairName --query "KeyMaterial" --output text > ~/.ssh/id_rsa && \
                        chmod 400 ~/.ssh/id_rsa && \
                        echo KeyPair $KeyPairName has been created.'

curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && \
chmod 755 ./kubectl && mv ./kubectl /usr/local/bin/kubectl
runuser -l ec2-user -c 'kubectl version --client'

echo Leaving user_data_bastion.sh

