from aws_cdk import (
    aws_ec2 as ec2,
    core
)

class PrivateInstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, inst_sg: ec2.SecurityGroup, ep_sg:ec2.CfnSecurityGroup, keyname: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        priv_inst_1 = ec2.Instance(self,'private-instance-1',
            instance_type=ec2.InstanceType('t2.micro'),
            machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            ),
            vpc=vpc,
            key_name=keyname,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            security_group=inst_sg
        )

        vpcendpoint = ec2.InterfaceVpcEndpoint(self, 'kVPCEndpoint',
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService('com.amazonaws.'+self.region+'.cloudformation',443),
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            security_groups=[ep_sg]
        )