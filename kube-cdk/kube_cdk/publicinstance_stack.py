from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    core
)

with open('./user_data/user_data_public.sh') as f:
    user_data_public = f.read()

class PublicInstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, inst_sg: ec2.SecurityGroup, role: iam.IRole, keyname: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        asg = autoscaling.AutoScalingGroup(self,"PublicInstanceASG",
             role=role,
             vpc=vpc,
             instance_type=ec2.InstanceType(instance_type_identifier="t2.small"),
             machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
             ),
             user_data=ec2.UserData.custom(user_data_public),
             key_name=keyname,
             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
             desired_capacity=3,
             max_capacity=3,
             min_capacity=3,
             security_group=inst_sg
        )

