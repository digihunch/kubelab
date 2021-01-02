from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    core
)

instance_type="t2.small"

with open('./script/user_data_public.sh') as f:
    user_data_public = f.read()

class PublicStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, inst_sg: ec2.SecurityGroup, role: iam.IRole, keyname: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cfnhup_restart_handle = ec2.InitServiceRestartHandle()
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_autoscaling/AutoScalingGroup.html#aws_cdk.aws_autoscaling.AutoScalingGroup.apply_cloud_formation_init
        # Note that configuring init metadata also implies that
        # cfn-init and cfn-signal are implicitly added to UserData. Signals property must be configured
        # creation policy is updated to wait for cfn-init to finish. (no need to specify in user data)
        asg = autoscaling.AutoScalingGroup(self,"PublicInstanceASG",
            role=role,
            vpc=vpc,
            instance_type=ec2.InstanceType(instance_type_identifier=instance_type),
            machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            ),
            user_data=ec2.UserData.custom(core.Fn.sub(user_data_public)),
            key_name=keyname,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            desired_capacity=2,
            max_capacity=2,
            min_capacity=2,
            signals=autoscaling.Signals.wait_for_all(timeout=core.Duration.minutes(5)),
            security_group=inst_sg
        )
        asg_logical_id=str(asg.node.default_child.logical_id)
        #print("logical id:"+str(asg.node.default_child.logical_id))
        #print("logical id:"+asg.auto_scaling_group_name)
        # The shell environment variable $ASGLOGICALID was set correctly in UserData, and persisted to when config set is executed with ec2.InitCommand. 
        # However, I had a hard time accessing logical resource ID of AutoScalingGroup because ec2.InitFile does not replace shell environment variable with actual value.
        # I have tried all the followings to no avail:
        #    1. When referenced as ${ASGLOGICALID} or as "${ASGLOGICALID}", it was interpreted as a literal resource name and cause ValidationError
        #    2. When referenced as $ASGLOGICALID, it was interpreted 
        # As a result, I had to split the initialization of asg into three steps.
        #    1. initialize asg without init, or init_options
        #    2. store logical ID of asg into python variable asg_logical_id
        #    3. add init and init_options to asg, which uses the value of asg_logical_id.
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
                        ec2.InitCommand.shell_command("echo configset thinks ASGLOGICALID=$ASGLOGICALID")
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
        #core.CfnOutput(self, "cfnasg", value='cfnasg: '+asg.node.default_child.to_string())
        #core.CfnOutput(self, "asg", value='asg: '+asg.to_string())
