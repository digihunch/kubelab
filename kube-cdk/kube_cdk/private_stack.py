from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    core
)

with open('./script/user_data_private.sh') as f:
    user_data_private = f.read()

class PrivateStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, inst_sg: ec2.SecurityGroup, ep_sg:ec2.CfnSecurityGroup, role: iam.IRole, keyname: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpcendpoint = ec2.InterfaceVpcEndpoint(self, 'kVPCEndpoint',
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService('com.amazonaws.'+self.region+'.cloudformation',443),
            private_dns_enabled=True,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            security_groups=[ep_sg]
        )

        cfnhup_restart_handle = ec2.InitServiceRestartHandle()

        asg = autoscaling.AutoScalingGroup(self, "PrivateInstanceASG",
            role=role,
            vpc=vpc,
            instance_type=ec2.InstanceType(instance_type_identifier="t2.small"),
            machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            ),
            user_data=ec2.UserData.custom(core.Fn.sub(user_data_private)),
            key_name=keyname,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            desired_capacity=5,
            max_capacity=5,
            min_capacity=5,
            signals=autoscaling.Signals.wait_for_all(timeout=core.Duration.minutes(5)),
            security_group=inst_sg
        )
        asg_logical_id=str(asg.node.default_child.logical_id)
        # check publicinstance_stack.py at this position for more comments.
        asg.apply_cloud_formation_init(ec2.CloudFormationInit.from_config_sets(
                config_sets={
                    "config_set_1":["config_step1","config_step2"],
                    "config_set_2":["config_step3","config_step4","config_step5"]
                },
                configs={
                    "config_step1": ec2.InitConfig([
                        ec2.InitPackage.yum("git")
                    ]),
                    "config_step2": ec2.InitConfig([
                        ec2.InitCommand.shell_command("echo configset execution.")
                    ]),
                    "config_step3": ec2.InitConfig([
                        ec2.InitFile.from_string(
                            file_name="/etc/cfn/hooks.d/cfn-auto-reloader.conf",
                            content=core.Fn.sub('\n'.join((
                                "[cfn-auto-reloader-hook]",
                                "triggers=post.update",
                                "path=Resources."+asg_logical_id+".Metadata.AWS::CloudFormation::Init",
                                "action=/opt/aws/bin/cfn-init -v --stack ${AWS::StackName} --resource "+asg_logical_id+" --configsets config_set_1,config_set_2"
                            ))),
                            group='root',
                            owner='root',
                            mode='000644',
                            service_restart_handles=[cfnhup_restart_handle]
                        )
                    ]),
                    "config_step4": ec2.InitConfig([
                        ec2.InitFile.from_string(
                            file_name="/etc/cfn/cfn-hup.conf",
                            content=core.Fn.sub('\n'.join((
                                "[main]",
                                "stack=${AWS::StackId}",
                                "region=${AWS::Region}",
                                "verbose=true",
                                "interval=5"
                            ))),
                            owner='root',
                            group='root',
                            mode='000644',
                            service_restart_handles=[cfnhup_restart_handle]
                        )
                    ]),
                    "config_step5": ec2.InitConfig([
                        ec2.InitService.enable(
                            service_name='cfn-hup',
                            enabled=True,
                            ensure_running=True,
                            service_restart_handle=cfnhup_restart_handle
                        )
                    ])
                }
            ),
            config_sets=["config_set_1","config_set_2"],
            print_log=True
        )
        core.CfnOutput(self, "Output", value='logical resource id of asg: '+str(asg.node.default_child.logical_id))