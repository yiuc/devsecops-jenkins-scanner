from typing import Dict

from aws_cdk import (
    aws_ec2 as ec2,
)

from constructs import Construct
from aws_cdk import App, Stack 

from .vpc import Vpc
from .security_group import SecurityGourp


class NetworkStack(Stack):
    vpc: ec2.IVpc
    es_sg_id: str

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpcConstruct = Vpc(self, 'Vpc')
        self.vpc = vpcConstruct.vpc

        sg = SecurityGourp(self, "SecurityGroups", self.vpc)
        self.es_sg_id = sg.es_sg.security_group_id
