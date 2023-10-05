from aws_cdk import (
    aws_ec2 as ec2
)

from constructs import Construct
from aws_cdk import App, Stack 


class SecurityGourp(Construct):
    _vpc: ec2.Vpc
    es_sg: ec2.SecurityGroup

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc) -> None:
        super().__init__(scope, id)

        self._vpc = vpc
        self.__create_es_sg()

    # Create elasticsearch security group
    def __create_es_sg(self) -> ec2.SecurityGroup:
        self.es_sg = ec2.SecurityGroup(
            self, 'ecs',
            security_group_name='ecs',
            vpc=self._vpc,
            description='ecs security group',
        )
