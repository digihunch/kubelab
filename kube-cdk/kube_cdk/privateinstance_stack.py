from aws_cdk import (
    aws_ec2 as ec2,
    #aws_ssm as ssm,
    core
)

class PrivateInstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, inst_sg: ec2.SecurityGroup, ep_sg:ec2.CfnSecurityGroup, **kwargs) -> None:
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
            key_name='cskey',
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE
            ),
            
            security_group=inst_sg
        )

        # priv_inst_2 = ec2.Instance(self,'private-instance-2',
        #     instance_type=ec2.InstanceType('t2.micro'),
        #     machine_image=ec2.AmazonLinuxImage(
        #         edition=ec2.AmazonLinuxEdition.STANDARD,
        #         generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        #         virtualization=ec2.AmazonLinuxVirt.HVM,
        #         storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        #     ),
        #     vpc=vpc,
        #     key_name='cskey',
        #     vpc_subnets=ec2.SubnetSelection(
        #         subnet_type=ec2.SubnetType.PRIVATE
        #     ),
        #     security_group=inst_sg
        # )

        # priv_inst_3 = ec2.Instance(self,'private-instance-3',
        #     instance_type=ec2.InstanceType('t2.micro'),
        #     machine_image=ec2.AmazonLinuxImage(
        #         edition=ec2.AmazonLinuxEdition.STANDARD,
        #         generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        #         virtualization=ec2.AmazonLinuxVirt.HVM,
        #         storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        #     ),
        #     vpc=vpc,
        #     key_name='cskey',
        #     vpc_subnets=ec2.SubnetSelection(
        #         subnet_type=ec2.SubnetType.PRIVATE
        #     ),
        #     security_group=inst_sg
        # )

        cfnendpoint = ec2.CfnVPCEndpoint(self, 'kVPCEndpoint',
            vpc_id=vpc.vpc_id,
            service_name='com.amazonaws.'+self.region+'.cloudformation',
            vpc_endpoint_type=ec2.VpcEndpointType.INTERFACE.value,
            private_dns_enabled=True,
            subnet_ids=[sn.subnet_id for sn in vpc.private_subnets],
            security_group_ids=[
                'endpointsg'
            ]
        )