from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)

with open('./user_data/user_data_bastion.sh') as f:
    user_data_bastion = f.read()

class BastionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, bstn_sg: ec2.SecurityGroup, role: iam.IRole, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/ApplyCloudFormationInitOptions.html#applycloudformationinitoptions
        # Note, if CloudFormationInit is specified, with config_sets, then config_sets are implicitly activated via ApplyCloudFormationInitOptions
        # There is no need to explicitly call cfn-init with configset in UserData script because it's done implicitly!
        bastion_host = ec2.Instance(self,'bastion-host',
            instance_type=ec2.InstanceType('t2.micro'),
            machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            ),
            vpc=vpc,
            role=role,
            user_data=ec2.UserData.custom(core.Fn.sub(user_data_bastion)),
            key_name='cskey',
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=bstn_sg,
            init=ec2.CloudFormationInit.from_config_sets(
                config_sets={
                    "config_set_1":["config_step1","config_step2"],
                    "config_set_2":["config_step3","config_step4"]
                },
                configs={
                    "config_step1": ec2.InitConfig([
                        ec2.InitPackage.yum("python3")
                    ]),
                    "config_step2": ec2.InitConfig([
                        ec2.InitPackage.yum("git")
                    ]),
                    "config_step3": ec2.InitConfig([
                        ec2.InitCommand.shell_command("git clone https://github.com/kubernetes-sigs/kubespray.git && chown -R ec2-user:ec2-user *",cwd="/home/ec2-user/")
                    ]),
                    "config_step4": ec2.InitConfig([
                        ec2.InitCommand.shell_command("amazon-linux-extras install -y ansible2")
                    ])
                }
            ),
            init_options=ec2.ApplyCloudFormationInitOptions(
                config_sets=["config_set_1","config_set_2"],
                #ignore_failures=True,
                print_log=True,
                timeout=core.Duration.minutes(10)
            )
        )
        self.pubkey = bastion_host.instance_id + '-pubkey'

        core.CfnOutput(self, "Output", value='ec2-user@'+bastion_host.instance_public_dns_name)

    #def __del__(self):
    #    print("destructor test")
