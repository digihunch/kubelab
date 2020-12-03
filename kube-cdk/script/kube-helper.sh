#! /usr/bin/bash
# AWS_REGION should be set in user profile
# reference: https://github.com/kubernetes-sigs/kubespray
declare -a IPS=""
for ID in $(aws autoscaling describe-auto-scaling-instances --query "AutoScalingInstances[?contains(AutoScalingGroupName,'PrivateInstanceASG')].InstanceId" --output text);
do 
    IPS+=($(aws ec2 describe-instances --instance-ids $ID --query Reservations[].Instances[].PrivateIpAddress --output text));
done

cd /home/ec2-user/kubespray 
CONFIG_FILE=inventory/mycluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
echo "Please run the command below to start configuration of kube nodes on ${IPS[@]}"
echo "cd kubespray && ansible-playbook -i inventory/mycluster/hosts.yaml cluster.yml -b -v"   # must run ansible-playbook from kubespray directory in order to use the config in there.
mkdir -p /home/ec2-user/.kube
echo "The configuration will take about 10 minutes. Then configure kubectl on this vm by running:"
echo "ansible node1 -m fetch -a \"src=/root/.kube/config dest=/home/ec2-user/.kube/config flat=yes\" -i inventory/mycluster/hosts.yaml --become"
