from jenkins.jenkins import JenkinsMasterStack
from network_stack.network_stack import NetworkStack
from codebuild_stack.codebuild import CodeBuildStack
from aws_cdk import App, Stack
import aws_cdk as cdk
import os

app = App()
network_stack = NetworkStack(
    app,
    "NetworkStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
        region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
    ),
)
jenkins_stack = JenkinsMasterStack(
    app,
    "JenkinsMasterStack",
    vpc=network_stack.vpc,
    env=cdk.Environment(
        account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
        region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
    ),
)

codebuild_stack = CodeBuildStack(
    app,
    "CodeBuildStack",
    vpc=network_stack.vpc,
    env=cdk.Environment(
        account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
        region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
    ),
)

app.synth()
