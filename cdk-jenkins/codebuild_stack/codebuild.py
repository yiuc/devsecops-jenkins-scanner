# create a codebuild cdk stack
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_ec2 as ec2,
    aws_s3 as s3,
)
import aws_cdk as cdk
import os


class CodeBuildStack(Stack):
    # define the __init__ method
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        repo_name: str = None,
        vpc: ec2.Vpc = None,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # create s3 bucket the name is jeknins-build-artifacts
        s3_bucket = s3.Bucket(
            self, "jenkins-build-artifacts", 
            auto_delete_objects=True,
            encryption=s3.BucketEncryption.UNENCRYPTED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # CodeBuild project that builds the webgoat jar
        codebuild_jar = codebuild.Project(
            self,
            "BuildImage",
            build_spec=codebuild.BuildSpec.from_asset("codebuild_webgoat_buildspec.yaml"),
            source=codebuild.Source.git_hub(owner="WebGoat", repo="WebGoat"),
            #artifacts=codebuild.Artifacts.s3(bucket=s3_bucket,package_zip=True,encryption=False),
            artifacts=codebuild.Artifacts.s3(bucket=s3_bucket,encryption=False),
            environment=codebuild.BuildEnvironment(
                privileged=True,
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5
            ),
            environment_variables={
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(
                    value=os.getenv("CDK_DEFAULT_ACCOUNT") or ""
                ),
                "REGION": codebuild.BuildEnvironmentVariable(
                    value=os.getenv("CDK_DEFAULT_REGION") or ""
                ),
            },
        )

        # cfn_codebuild = build_jar.node.default_child
        # cfn_codebuild.override_logical_id("codebuildbuildimagetest123")

        # Grants CodeBuild project access to pull/push from s3
        s3_bucket.grant_read_write(codebuild_jar)