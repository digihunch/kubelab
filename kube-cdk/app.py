#!/usr/bin/env python3

from aws_cdk import core

from kube_cdk.kube_cdk_stack import KubeCdkStack


app = core.App()
KubeCdkStack(app, "kube-cdk")

app.synth()
