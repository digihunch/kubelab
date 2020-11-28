#!/usr/bin/env python3

from aws_cdk import core

from kube_cdk.kube_cdk_stack import KubeCdkStack
from kube_cdk.security_stack import SecurityStack
from kube_cdk.bastion_stack import BastionStack
from kube_cdk.kms_stack import KMSStack


app = core.App()
kube_cdk_stack = KubeCdkStack(app, "kube-cdk")
security_stack = SecurityStack(app, 'security-stack', vpc=kube_cdk_stack.vpc)
bastion_stack = BastionStack(app, 'bastion', vpc=kube_cdk_stack.vpc, sg=security_stack.bastion_sg)
kms_stack = KMSStack(app,'kms-stack')
app.synth()
