#! /usr/bin/bash
# AWS_REGION should be set in user profile
# reference: https://github.com/kubernetes-sigs/kubespray
declare -a IPS=""
for ID in $(aws autoscaling describe-auto-scaling-instances --query "AutoScalingInstances[?contains(AutoScalingGroupName,'PrivateInstanceASG')].InstanceId" --output text);
do
    IPS+=($(aws ec2 describe-instances --instance-ids $ID --query Reservations[].Instances[].PrivateIpAddress --output text));
done

export CONFIG_FILE=inventory/mycluster/hosts.yaml
python3 contrib/inventory_builder/inventory.py ${IPS[@]}
sed -i '/^\[defaults\]$/a inventory = '"$CONFIG_FILE" ansible.cfg
echo "Please run the command below to start configuration of kube nodes on ${IPS[@]}"
echo "ansible-playbook cluster.yml -b -v | tee /tmp/kcluster.log"
echo "ansible-playbook setup-kubectl-local.yml -v"
