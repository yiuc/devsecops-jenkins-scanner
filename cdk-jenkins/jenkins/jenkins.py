from aws_cdk import (
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_iam as iam,
)
from constructs import Construct
from aws_cdk import App, Stack, CfnOutput
from aws_cdk import RemovalPolicy, Duration


class JenkinsMasterStack(Stack):
    # def __init__(self, scope: Construct, id: str, **kwargs) -> None:
    #     super().__init__(scope, id, **kwargs)

    def __init__(self, scope: Construct, id: str, *, vpc: ec2.Vpc = None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cluster = ecs.Cluster(
            self, "jenkins-cluster", vpc=vpc, cluster_name="jenkins-cluster"
        )

        file_system = efs.FileSystem(
            self, "JenkinsFileSystem", vpc=vpc, removal_policy=RemovalPolicy.DESTROY
        )

        access_point = file_system.add_access_point(
            "AccessPoint",
            path="/jenkins-home",
            posix_user={
                "uid": "1000",
                "gid": "1000",
            },
            create_acl=efs.Acl(owner_gid="1000", owner_uid="1000", permissions="755"),
        )

        # add a policystatement to allow access codebuild
        codebuild_policy = iam.PolicyStatement.from_json({
            "Effect": "Allow",
            "Action": ["codebuild:*","s3:*"],
            "Resource": "*"
        })

        task_definition = ecs.FargateTaskDefinition(
            self,
            "jenkins-task-definition",
            memory_limit_mib=4096,
            cpu=2048,
            family="jenkins",
        )

        task_definition.add_volume(
            name="jenkins-home",
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=file_system.file_system_id,
                transit_encryption="ENABLED",
                authorization_config=ecs.AuthorizationConfig(
                    access_point_id=access_point.access_point_id, iam="ENABLED"
                ),
            ),
        )

        task_definition.add_to_task_role_policy(codebuild_policy)
        task_definition.add_to_execution_role_policy(codebuild_policy)

        ecr_repository = ecr.Repository.from_repository_name(
            self, "jenkins-master", "jenkins-master")

        container_definition = task_definition.add_container(
            "jenkins",
            #image=ecs.ContainerImage.from_registry("jenkins/jenkins:lts"),
            image = ecs.ContainerImage.from_ecr_repository(ecr_repository, tag="1"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="jenkins"),
        )

        container_definition.add_mount_points(
            ecs.MountPoint(
                container_path="/var/jenkins_home",
                read_only=False,
                source_volume="jenkins-home",
            )
        )

        container_definition.add_port_mappings(
            ecs.PortMapping(
                container_port=8080,
                host_port=8080,
            )
        )

        # add security group to cluster
        service_security_group = ec2.SecurityGroup(
            self,"service_security_group", vpc=vpc
        )
        
        service_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"), connection=ec2.Port.all_traffic()
        )
        service = ecs.FargateService(
            self,
            "JenkinsService",
            cluster=cluster,
            security_groups=[service_security_group],
            task_definition=task_definition,
            desired_count=1,
            max_healthy_percent=100,
            min_healthy_percent=0,
            health_check_grace_period=Duration.minutes(5),
        )

        service.connections.allow_to(file_system, ec2.Port.tcp(2049))

        ecs_security_group = ec2.SecurityGroup(
            self, "cdk-jenkins-security-group", vpc=vpc
        )
        current_ip = self.node.try_get_context("current_ip")
        if current_ip:
            ecs_security_group.add_ingress_rule(
                ec2.Peer.ipv4(f"{current_ip}/32"), ec2.Port.tcp(443)
            )
            ecs_security_group.add_ingress_rule(
                ec2.Peer.ipv4(f"{current_ip}/32"), ec2.Port.tcp(80)
            )

        certificate_arn = self.node.try_get_context("certificateArn")
        if certificate_arn:
            load_balancer = elbv2.ApplicationLoadBalancer(
                self,
                "LoadBalancer",
                vpc=vpc,
                internet_facing=True,
                security_group=ecs_security_group,
            )
            CfnOutput(
                self, "LoadBalancerDNSName", value=load_balancer.load_balancer_dns_name
            )

            listener = load_balancer.add_listener(
                "Listener",
                port=443,
                certificates=[
                    elbv2.ListenerCertificate(certificate_arn=certificate_arn)
                ],
                protocol=elbv2.ApplicationProtocol.HTTPS,
                open=False,
                ssl_policy=elbv2.SslPolicy.FORWARD_SECRECY_TLS12_RES_GCM,
            )

            listener.add_targets(
                "JenkinsTarget",
                port=8080,
                targets=[service],
                deregistration_delay=Duration.seconds(10),
                health_check={"path": "/login"},
            )

            hosted_zone_name = self.node.try_get_context("hostedZoneName")
            if hosted_zone_name:
                hosted_zone = route53.HostedZone.from_lookup(
                    self, "HostedZone", domain_name=hosted_zone_name
                )
                route53.CnameRecord(
                    self,
                    "CnameRecord",
                    zone=hosted_zone,
                    record_name="jenkins",
                    domain_name=load_balancer.load_balancer_dns_name,
                    ttl=Duration.minutes(1),
                )
        else:
            load_balancer = elbv2.NetworkLoadBalancer(
                self,
                "LoadBalancer",
                vpc=vpc,
                internet_facing=True,
                cross_zone_enabled=True
            )

            CfnOutput(
                self, "LoadBalancerDNSName", value=load_balancer.load_balancer_dns_name
            )

            cfnlb = load_balancer.node.default_child
            cfnlb.add_property_override("SecurityGroups", [ecs_security_group.security_group_id]);

            listener = load_balancer.add_listener(
                "Listener",
                port=80,
                protocol=elbv2.Protocol.TCP,
            )

            group = listener.add_targets(
                "JenkinsTarget",
                port=8080,
                targets=[service],
                deregistration_delay=Duration.seconds(10),
            )

            group.configure_health_check(
                path="/login",
                port="8080",
                protocol=elbv2.Protocol.HTTP,
                healthy_http_codes="200"
            )
