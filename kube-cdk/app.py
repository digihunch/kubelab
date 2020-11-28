#!/usr/bin/env python3

from aws_cdk import core

from kube_cdk.vpc_stack import VPCStack
from kube_cdk.security_stack import SecurityStack
from kube_cdk.publicinstance_stack import PublicInstanceStack
from kube_cdk.privateinstance_stack import PrivateInstanceStack


app = core.App()
vpc_stack = VPCStack(app, "vpc-stack")
security_stack = SecurityStack(app, 'security-stack', vpc=vpc_stack.vpc)
publicinstance_stack = PublicInstanceStack(app,'public-instance-stack', vpc=vpc_stack.vpc, inst_sg=security_stack.public_sg, bstn_sg=security_stack.bastion_sg, role=security_stack.instance_role)
privateinstance_stack = PrivateInstanceStack(app,'private-instance-stack', vpc=vpc_stack.vpc, inst_sg=security_stack.private_sg, ep_sg=security_stack.endpoint_sg)
app.synth()
