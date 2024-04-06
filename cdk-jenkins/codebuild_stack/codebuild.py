# create a codebuild cdk stack
from aws_cdk import Stack, CfnOutput
from constructs import Construct
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_ec2 as ec2,
    aws_ecr as ecr,
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

        joern_ecr_repository = ecr.Repository.from_repository_name(
            self, "joern-scanner", "joern-scanner"
        )

        # create a ecr repository the name is behave-image and variable is behave_ecr_repository
        behave_ecr_repository = ecr.Repository(
            self,
            "behave-image",
            image_scan_on_push=True,
            image_tag_mutability=ecr.TagMutability.MUTABLE,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # create s3 bucket the name is jeknins-build-artifacts
        s3_bucket = s3.Bucket(
            self,
            "jenkins-build-artifacts",
            auto_delete_objects=True,
            encryption=s3.BucketEncryption.UNENCRYPTED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # CodeBuild project that builds the webgoat jar
        codebuild_jar = codebuild.Project(
            self,
            "BuildImage",
            build_spec=codebuild.BuildSpec.from_asset(
                "codebuild_webgoat_buildspec.yaml"
            ),
            source=codebuild.Source.git_hub(owner="WebGoat", repo="WebGoat"),
            # artifacts=codebuild.Artifacts.s3(bucket=s3_bucket,package_zip=True,encryption=False),
            artifacts=codebuild.Artifacts.s3(bucket=s3_bucket, encryption=False),
            environment=codebuild.BuildEnvironment(
                privileged=True,
                compute_type=codebuild.ComputeType.MEDIUM,
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
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

        # code build project for execute joern
        codebuild_joern = codebuild.Project(
            self,
            "JoernScan",
            build_spec=codebuild.BuildSpec.from_asset("codebuild_joern_buildspec.yaml"),
            source=codebuild.Source.s3(
                bucket=s3_bucket, path="BuildImage74257FD8-G2bjbCQI8qQK/59/results.zip"
            ),
            environment=codebuild.BuildEnvironment(
                privileged=True,
                compute_type=codebuild.ComputeType.LARGE,
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
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
        joern_ecr_repository.grant_pull(codebuild_joern)

        # code build project for execute codebuild_behave_image_build_buildspec.yaml
        codebuild_behave_image_build = codebuild.Project(
            self,
            "BehaveImageBuild",
            build_spec=codebuild.BuildSpec.from_asset(
                "codebuild_behave_image_build_buildspec.yaml"
            ),
            source=codebuild.Source.git_hub(
                owner="yiuc", repo="devsecops-jenkins-scanner", branch_or_ref="develop"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
                compute_type=codebuild.ComputeType.MEDIUM,
                privileged=True,
            ),
            environment_variables={
                "ECR_URL": codebuild.BuildEnvironmentVariable(
                    value=behave_ecr_repository.repository_uri
                ),
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(
                    value=os.getenv("CDK_DEFAULT_ACCOUNT") or ""
                ),
            },
        )
        behave_ecr_repository.grant_pull_push(codebuild_behave_image_build)

        # code build project for execute codebuild_behave_scanning_buildspec.yaml
        codebuild_behave_scanning = codebuild.Project(
            self,
            "BehaveScanning",
            build_spec=codebuild.BuildSpec.from_asset(
                "codebuild_behave_scanning_buildspec.yaml"
            ),
            source=codebuild.Source.git_hub(
                owner="yiuc", repo="devsecops-jenkins-scanner", branch_or_ref="develop"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
                compute_type=codebuild.ComputeType.MEDIUM,
                privileged=True,
            ),
            environment_variables={
                "ECR_URL": codebuild.BuildEnvironmentVariable(
                    value=behave_ecr_repository.repository_uri
                ),
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(
                    value=os.getenv("CDK_DEFAULT_ACCOUNT") or ""
                ),
                "APP_URL": codebuild.BuildEnvironmentVariable(
                    value="http://webgoat.svc.test.local:8080"
                ),
            },
            vpc=vpc,
        )
        behave_ecr_repository.grant_pull(codebuild_behave_scanning)

        codebuild_gaulant = codebuild.Project(
            self,
            "GauntltTest",
            build_spec=codebuild.BuildSpec.from_asset(
                "codebuild_gauntlt_buildspec.yaml"
            ),
            source=codebuild.Source.git_hub(
                owner="yiuc", repo="devsecops-jenkins-scanner"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
                compute_type=codebuild.ComputeType.MEDIUM,
                privileged=True,
            ),
            vpc=vpc,
        )

        # cfn_codebuild = build_jar.node.default_child
        # cfn_codebuild.override_logical_id("codebuildbuildimagetest123")

        # Grants CodeBuild project access to pull/push from s3
        s3_bucket.grant_read_write(codebuild_jar)
        s3_bucket.grant_read_write(codebuild_joern)
        s3_bucket.grant_read_write(codebuild_behave_image_build)
        s3_bucket.grant_read_write(codebuild_behave_scanning)

        CfnOutput(self, "WebGoatBuildProjectName", value=codebuild_jar.project_name)
        CfnOutput(self, "JoernScanProjectName", value=codebuild_joern.project_name)
        CfnOutput(self, "GauntltProjectName", value=codebuild_gaulant.project_name)
        CfnOutput(self, "BehaveImageBuildProjectName", value=codebuild_behave_image_build.project_name)
        CfnOutput(self, "BehaveScanningProjectName", value=codebuild_behave_scanning.project_name)
        CfnOutput(self, "BehaveECR",value=behave_ecr_repository.repository_uri)
        CfnOutput(self, "S3ArtifactName", value=s3_bucket.bucket_name)
