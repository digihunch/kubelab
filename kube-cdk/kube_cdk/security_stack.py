from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    core
)

class SecurityStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str,vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        self.bastion_sg = ec2.SecurityGroup(self, 'bastionsg',
            security_group_name='bastion-sg',
            vpc=vpc,
            description="SG for Bastion Host",
            allow_all_outbound=True
        )

        self.bastion_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22),"SSH Access")

        instance_role = iam.Role(self, 'instanceprofile',
            assumed_by=iam.ServicePrincipal(service='lambda.amazonaws.com'),
            role_name='ec2-role',
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name='service-role/AWSLambdaBasicExecutionRole'
            )]
        )