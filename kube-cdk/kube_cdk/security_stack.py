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

        self.public_sg = ec2.SecurityGroup(self, 'publicsg',
            security_group_name='public-sg',
            vpc=vpc,
            description="SG for public instances",
            allow_all_outbound=True
        )

        self.private_sg = ec2.SecurityGroup(self, 'privatesg',
            security_group_name='private-sg',
            vpc=vpc,
            description="SG for private instances",
            allow_all_outbound=True
        )

        self.bastion_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22),"SSH Access")

        self.instance_role = iam.Role(self, 'instancerole',
            assumed_by=iam.ServicePrincipal(service='ec2.amazonaws.com'),
            role_name='ec2-role',
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name='AmazonEC2ReadOnlyAccess'
            )]
        )

        self.instance_role.add_to_policy(
            statement=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['ec2:ImportKeyPair','ec2:CreateKeyPair','ec2:DescribeKeyPairs','ec2:DeleteKeyPair'],
                resources=['*']
            )
        )