from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    #aws_ssm as ssm,
    core
)

with open('./user_data/user_data.sh') as f:
    user_data = f.read()

class PublicInstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, inst_sg: ec2.SecurityGroup, bstn_sg: ec2.SecurityGroup, role: iam.IRole, **kwargs) -> None:
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
             user_data=ec2.UserData.custom(user_data),
             key_name='cskey',
             vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
             ),
             desired_capacity=3,
             max_capacity=3,
             min_capacity=3,
             security_group=inst_sg
        )

        bastion_host = ec2.Instance(self,'bastion-host',
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
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            security_group=bstn_sg
        )