# kubelab
Kubernetes Lab Infrastructure

To install or update aws-cdk, you need npm:
npm install -g aws-cdk
npm update -g aws-cdk

If you need to initialize a project, creat empty directory and from within the directory, run:
ckd init app --language python

Start virtual environment
source .venv/bin/activate

To install dependent python packages. Run:
pip install -r requirements.txt

You can check available packages with
pip list


From bastion host, to find out IP addresses, run:
AWS_REGION=$(aws configure get region)
for ID in $(aws autoscaling describe-auto-scaling-instances --region $AWS_REGION --query 'AutoScalingInstances[?contains(AutoScalingGroupName,`PrivateInstanceASG`)].InstanceId' --output text);
do
aws ec2 describe-instances --instance-ids $ID --region $AWS_REGION --query Reservations[].Instances[].PrivateIpAddress --output text
done


https://kubernetes.io/docs/setup/production-environment/tools/kubespray/
https://github.com/kubernetes-sigs/kubespray/blob/master/docs/getting-started.md#building-your-own-inventory
