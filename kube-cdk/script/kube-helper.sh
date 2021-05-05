#! /usr/bin/bash
# AWS_REGION should be set in user profile
# reference: https://github.com/kubernetes-sigs/kubespray
declare -a IPS=""
for ID in $(aws autoscaling describe-auto-scaling-instances --query "AutoScalingInstances[?contains(AutoScalingGroupName,'PrivateInstanceASG')].InstanceId" --output text);
do
    IPS+=($(aws ec2 describe-instances --instance-ids $ID --query Reservations[].Instances[].PrivateIpAddress --output text));
done

CONFIG_FILE=inventory/mycluster/hosts.yaml
python3 contrib/inventory_builder/inventory.py ${IPS[@]}
sed -i '/^\[defaults\]$/a inventory = '"$CONFIG_FILE" ansible.cfg
sed -i '/Stop if unknown OS/,+6d' ./roles/kubernetes/preinstall/tasks/0020-verify-settings.yml # remove OS check because Amazon is not on the list
export ANSIBLE_CONFIG=$(realpath ansible.cfg)

echo "Please run the command below to start configuration of kube nodes on ${IPS[@]}"
echo "ansible-playbook cluster.yml -b -v"
echo "ansible-playbook setup-kubectl-local.yml -v"
