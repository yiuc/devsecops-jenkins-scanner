from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_lambda as lambda_,
    aws_ecs as ecs,
    aws_servicediscovery as servicediscovery,
    aws_ec2 as ec2,
)

from constructs import Construct
from aws_cdk import App, Stack


class ECSstack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        repo_name: str = None,
        vpc: ec2.Vpc = None,
        lambda_code: lambda_.CfnParametersCode = None,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        taskDefinition = ecs.TaskDefinition(
            self,
            "ECSTaskDefinition",
            compatibility=ecs.Compatibility.FARGATE,
            cpu="1024",
            memory_mib="2048",
        )

        webgoattaskDefinition = ecs.TaskDefinition(
            self,
            "WebGoatECSTaskDefinition",
            compatibility=ecs.Compatibility.FARGATE,
            cpu="1024",
            memory_mib="2048",
        )

        ecs_security_group = ec2.SecurityGroup(self, "cdk-fargate-example", vpc=vpc)
        ecs_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(3000)
        )
        ecs_security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(8080)
        )

        ecscluster = ecs.Cluster(
            self,
            "Cluster",
            container_insights=True,
            enable_fargate_capacity_providers=True,
            vpc=vpc,
        )

        # service discovery creation
        sd_namespace = ecscluster.add_default_cloud_map_namespace(
            name="svc.test.local", vpc=vpc
        )
        servicediscovery.Service(
            self, "svc.test.local", namespace=sd_namespace, load_balancer=True
        )

        taskDefinition.add_container(
            id="AppContainer",
            image=ecs.ContainerImage.from_registry("owasp/railsgoat:rails_5"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="gauntlt"),
            port_mappings=[ecs.PortMapping(container_port=3000)],
            command=["sh", "-c", "rails db:setup && rails server -b 0.0.0.0"],
        )

        webgoattaskDefinition.add_container(
            id="AppContainer",
            image=ecs.ContainerImage.from_registry("webgoat/webgoat-7.1"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="webgoat"),
            port_mappings=[ecs.PortMapping(container_port=8080)],
        )

        ecs_fargate_sg = ec2.SecurityGroup.from_security_group_id(
            self, "fargate_sg", ecs_security_group.security_group_id
        )

        ecs.FargateService(
            self,
            "EcsService",
            task_definition=taskDefinition,
            security_groups=[ecs_fargate_sg],
            cluster=ecscluster,
            cloud_map_options=ecs.CloudMapOptions(
                cloud_map_namespace=sd_namespace, name="railsgoat"
            ),
        )

        ecs.FargateService(
            self,
            "EcsWebGoatService",
            task_definition=webgoattaskDefinition,
            security_groups=[ecs_fargate_sg],
            cluster=ecscluster,
            cloud_map_options=ecs.CloudMapOptions(
                cloud_map_namespace=sd_namespace, name="webgoat"
            ),
        )
