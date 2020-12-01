#!/usr/bin/env python3

from aws_cdk import core
from kube_cdk.vpc_stack import VPCStack
from kube_cdk.bastion_stack import BastionStack
from kube_cdk.security_stack import SecurityStack
from kube_cdk.public_stack import PublicStack
from kube_cdk.private_stack import PrivateStack


app = core.App()
vpc_stack = VPCStack(app, "vpc-stack")
security_stack = SecurityStack(app, 'security-stack', vpc=vpc_stack.vpc)
bastion_stack = BastionStack(app, 'bastion-stack', vpc=vpc_stack.vpc, bstn_sg=security_stack.bastion_sg, role=security_stack.instance_role)
#print(bastion_stack.pubkey)
public_stack = PublicStack(app,'public-stack', vpc=vpc_stack.vpc, inst_sg=security_stack.public_sg, role=security_stack.instance_role, keyname=bastion_stack.pubkey)
public_stack.add_dependency(bastion_stack)
private_stack = PrivateStack(app,'private-stack', vpc=vpc_stack.vpc, inst_sg=security_stack.private_sg, ep_sg=security_stack.endpoint_sg, role=security_stack.instance_role, keyname=bastion_stack.pubkey)
private_stack.add_dependency(bastion_stack)
app.synth()
