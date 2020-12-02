# KubeLab - prepare Kubernetes infrastructure on AWS 

While there is AKS, for learning at a closer distance it is beneficial to self-manage a cluster of K8s nodes, instead of a single node. This project provides Infrastructure as Code (AWS CDK in Python) to provision private instances on AWS, then provision the Kubernetes nodes with Kubespray.

# AWS CDK

AWS CDK is a development kit that can be used to generate CloudFormation template. It support a number of programming languages and significantly increase code reusability. To install or upgrade AWS CDK, you need npm:
> npm install -g aws-cdk
> npm update -g aws-cdk

To initialize a project, e.g. in Python, create an empty directory with project name(e.g. kubelab). Then run the following from within the directory:
> ckd init app --language python

In order to not mess up existing Python environment, we will use **virtual environment** for the project. To start virtual environment, run:
> source .venv/bin/activate

Within virtual environment, when we run the project for the first time after initialization, we need to install the pip3 packages as listed in requirements.txt. Make sure to include required packages for the project such as aws_cdk.aws_autoscaling in the txt. To install, run:
> pip install -r requirements.txt

We can load the code in Visual Studio code from within the directory:
> code .

We can now validate syntax with cdk, by running:
> cdk ls

To actually deploy a stack, we can run:
> cdk deploy vpc-stack

> cdk deploy security-stack

> cdk deploy bastion-stack

> cdk deploy private-stack

# The cluster
The kube-cdk directory includes the CDK files required to create Cloudformation stacks. The VCP stack provisions the public and private networks. The security stack includes security groups required for each instance. For example, on the private instances, it opens the ports that are required by Kubernetes Master and nodes, to the entire VPC. The bastion stack includes the bastion host, to be placed in public subnet. During creation of bastion host, it generates a new RSA key pair and ec2-user will use the newly generated private key. With the public key registered with AWS and used during the creation of other instances. It is expected that once you SSH to the bastion host, you can connect to any other instance with key authentication. 

# Kubespray

[Kubespray](https://kubernetes.io/docs/setup/production-environment/tools/kubespray/) is a project to simplify the configuration of Kubernetes nodes.  The configuration files are hosted in [this](https://github.com/kubernetes-sigs/kubespray) repository, and [this](https://github.com/kubernetes-sigs/kubespray/blob/master/docs/getting-started.md#building-your-own-inventory) is a good instruction.
By default, three EC2 instances (t2.small) will be created in private subnet to serve as Kubernetes cluster. The existing environment needs to meet the requirement as listed the documentation. I created a little helper script (kube-helper.sh) to smooth out this step. The helper script looks up on the autoscaling group for private instances, with IP address returned, the script uses the tool provided in Kubespray to configure the Ansible inventory.
The helper script will provide the command to run at the end, which is:
>cd kubespray && ansible-playbook -i inventory/mycluster/hosts.yaml cluster.yml -b -v

This will kick of the playbooks required for configuration on the target hosts. The configuration process should take about 10 minutes.


