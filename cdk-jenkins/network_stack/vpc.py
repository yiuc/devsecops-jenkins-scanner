from typing import Dict, List

from aws_cdk import (
    aws_ec2 as ec2
)

from constructs import Construct
from aws_cdk import App, Stack 


class Vpc(Construct):
    vpc: ec2.Vpc
    subnet_configuration: List[ec2.SubnetConfiguration] = []

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.__build_subnets_config()
        self.__create_vpc()

    def __create_vpc(self):
        self.vpc = ec2.Vpc(
            scope=self,
            id="ECSVPC",
            subnet_configuration=self.subnet_configuration,
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.18.0.0/16"),
            enable_dns_hostnames=True,
            enable_dns_support=True,
            nat_gateways=2,
        )

    def __build_subnets_config(self):
        self.subnet_configuration = [ec2.SubnetConfiguration(
            subnet_type=ec2.SubnetType.PUBLIC,
            name="Public",
            cidr_mask=24
        ),
            ec2.SubnetConfiguration(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            name="Private",
            cidr_mask=24
        )
        ]
