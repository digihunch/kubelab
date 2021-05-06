from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
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

        self.public_sg = ec2.SecurityGroup(self, 'publicsg',
            security_group_name='public-sg',
            vpc=vpc,
            description="SG for public instances",
            allow_all_outbound=True
        )
        self.public_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22),"SSH Access")
        self.public_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_icmp(),"Ping from VPC") 

        self.private_sg = ec2.SecurityGroup(self, 'privatesg',
            security_group_name='private-sg',
            vpc=vpc,
            description="SG for private instances",
            allow_all_outbound=True
        )
        self.private_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22),"SSH Access")
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.all_icmp(),"Ping from VPC") 
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.tcp(179),"TCP port required for BGP connectvity with calico plug")
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.tcp(6443),"TCP port required for kubernetes master")
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.tcp_range(2379,2380),"TCP port required for kubernetes master")
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.tcp_range(10250,10252),"TCP port required for kubernetes master")
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.tcp(10255),"TCP port required for kubernetes master AND node")
        # 10250 and 10255 are also required for node.
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.tcp_range(30000,32767),"TCP port required for kubernetes node")
        self.private_sg.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block),ec2.Port.tcp(6783),"TCP port required for kubernetes node")

        self.endpoint_sg = ec2.SecurityGroup(self, 'endpointsg',
            security_group_name='endpoint-sg',
            vpc=vpc,
            description="SG for VPC endpoint",
            allow_all_outbound=True
        )
        self.endpoint_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443),"VPC endpoint uses TCP port 443")

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
                actions=['ec2:ImportKeyPair','ec2:CreateKeyPair','ec2:DescribeKeyPairs'],  # 'ec2:DeleteKeyPair' isn't needed
                resources=['*']
            )
        )
        #self.instance_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM"))
