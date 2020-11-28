from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    aws_ssm as ssm,
    core
)

class PublicInstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, sg: ec2.SecurityGroup, role: iam.IRole, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        asg = autoscaling.AutoScalingGroup(self,"PublicInstanceASG",
             role=role,
             vpc=vpc,
             instance_type=ec2.InstanceType(instance_type_identifier="t2.micro"),
             machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
             ),
             key_name='yi_cs',
             vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
             ),
             desired_capacity=2,
             max_capacity=2,
             min_capacity=2
        )