import sys
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
    core
)


class KubeCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        prj_name=self.node.try_get_context("project_name")
        env_name=self.node.try_get_context("env")

        # The code that defines your stack goes here
        self.vpc = ec2.Vpc(self, 'kVPC',
            cidr='172.17.0.0/16',
            max_azs=2,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Isolate",
                    subnet_type=ec2.SubnetType.ISOLATED,
                    cidr_mask=24
                )
            ],
            nat_gateways=1
        )

        priv_subnets = [subnet.subnet_id for subnet in self.vpc.private_subnets]
        # for each subnet in self.vpc.private_subnets, assign subnet.subnet_id to list priv_subnets
        # this is a shorthand expression

        pscount = 1
        for ps in priv_subnets:
            ssm.StringParameter(self,'private-subnet-'+str(pscount),
                string_value=ps,
                parameter_name='/'+env_name+'/private-subnet-'+str(pscount)
            )
            pscount+=1
