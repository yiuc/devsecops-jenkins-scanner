# DevSecOps Jenkins Scanner

This guide provides step-by-step instructions for setting up a DevSecOps Jenkins scanner using AWS native services and Jenkins. Follow these instructions to automate security scanning in a WebGoat application using CDK for infrastructure provisioning and Jenkins DSL for pipeline configuration.

## 1 Objective

Software security vulnerabilities have become a major concern for enterprises, and introducing security testing and scanning tools into the CI/CD pipeline is a crucial step in their DevSecOps journey. However, while security scanners can be useful when configured correctly with rule customization, they often require advanced security and software engineering skills, such as understanding complex exploits and Abstract Syntax Trees (AST). Additionally, these tools may not cater to testing security-related business logic or application-specific corner cases, and they may lack the flexibility to manage complicated test cases at scale. As a result, many enterprises face challenges after starting their shift-left security initiatives because simply plugging in scanners and passing scan results to developers does not truly constitute a shift-left approach; it merely shifts responsibility.

Behavior-Driven Development (BDD) for security can be a lifesaver for software engineers dealing with security problems. Our sharing at the AWS Summit, "Dealing with Challenges of DevSecOps Practice in Enterprises" (https://hktw-resources.awscloud.com/aws-summit-hong-kong-2023/dealing-with-challenges-of-devsecops-practice-in-enterprises), introduced the concept of BDD security test automation and fuzzing techniques long practiced by big tech companies and major financial services institutions. In this guide, we will walk you through a hands-on lab where you can get your hands dirty and build your first security test cases.

The objective of this installation guide is to demonstrate how to use AWS native services and Jenkins to automate security scanning in a WebGoat application. The guide will cover the use of CDK for infrastructure provisioning and Jenkins DSL for pipeline configuration, providing a practical example of integrating security testing into the CI/CD pipeline.

## 2 Technical Stack

The following technical stack will be used in this installation:

- [CDK](https://aws.amazon.com/cdk/?nc1=h_ls) - Infrastructure as Code (IaC), provides a library of constructs that cover many AWS services and features
- Jenkins - Jenkins is an open source automation server that helps automate various parts of the software development process
    - [Jenkins Configuration as Code](https://abrahamntd.medium.com/automating-jenkins-setup-using-docker-and-jenkins-configuration-as-code-897e6640af9d)
    - Groovy
- [Codebuild](https://aws.amazon.com/codebuild/) - Fully managed build service used as a build server and Jenkins agent
    - [Integrating AWS CodeBuild into Jenkins pipelines](https://jenkinshero.com/integrating-aws-codebuild-into-jenkins-pipelines/)
- [Joern](https://github.com/joernio/joern) - A tool for analyzing source code, bytecode, and binary executables for security vulnerabilities
- [WebGoat](https://owasp.org/www-project-webgoat/) - An insecure web application designed for developers to test and learn about common web application vulnerabilities
- [Cognito](https://aws.amazon.com/pm/cognito/?gclid=Cj0KCQjw5cOwBhCiARIsAJ5njuZaZrIy83YnNcdVGENpaxz2SVGRhHFibhSvZdhRbt4JKv0iCS50qeQaApTjEALw_wcB&trk=0436ebd7-f0ca-404b-8936-e4ed264096c4&sc_channel=ps&ef_id=Cj0KCQjw5cOwBhCiARIsAJ5njuZaZrIy83YnNcdVGENpaxz2SVGRhHFibhSvZdhRbt4JKv0iCS50qeQaApTjEALw_wcB:G:s&s_kwcid=AL!4422!3!651541934827!e!!g!!cognito!19828212429!149982290871)
- [Behave](https://behave.readthedocs.io/en/latest/)

### 2.1 Overall Architecture

The infrastructure stack will be provisioned using CDK. Please refer to the provided architecture diagram for an overview of the overall architecture.
![](./docs/image/infra.drawio.png)

### 2.2 Folder Layout

The project has the following folder layout:

```
devsecops-jenkins-scanner
├── README.md
├── cdk-jenkins - CDK code
├── gauntlt - BDD scanning
├── behave - BDD scanning 
├── jenkins-master-image - Jenkins configuration file
└── local - local docker development
```

## 3 Prerequisites

Before starting the installation, ensure that the following prerequisites are met:

- An AWS account with CLI access (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)
- A Linux-based platform (Recommended: [AWS Cloud9](https://aws.amazon.com/pm/cloud9/))
- Docker installed
- Fork the https://github.com/yiuc/devsecops-jenkins-scanner repository under your GitHub account, as you will need to make changes to the repository

## 4 Provision AWS resources

Follow the steps below to install and configure the DevSecOps Jenkins scanner.

### 4.1 Provision Cloud9 as the Development Terminal

1. Create a new Cloud9 Environment through the AWS console.
2. Follow the instructions to provide the required inputs:
    - Name
    - Instance Type (Recommended: t3.small or more powerful)
    - Platform - Amazon Linux 2023
    - Use AWS Systems Manager (SSM) for connection
    - VPC can be the default VPC
3. Click on "Details" and "Manage EC2 Instance" to increase the storage to 30GB.
4. Open your Cloud9 instance in the console and start the configuration below.

#### 4.1.1 Manual Setup in Cloud9

1. Set up the environment:

    ```bash
    export AWS_PAGER= ;\
    export AWS_REGION=ap-southeast-1 ;\
    export ACCOUNT=$(aws sts get-caller-identity --out json --query 'Account' | sed 's/"//g') ;\
    export YOURID=YOUR GITHUB ID
    ```

2. Fork the GitHub repository, generate an SSH access key (`ssh-keygen -t rsa`), and add your SSH public key to the repository's "Deploy Keys" section to grant access rights.
3. Download the source code from your forked repository: `git clone git@github.com:$YOURID/devsecops-jenkins-scanner`
4. Modify the repository name: `find . -type f -exec sed -i "s/yiuc/$YOURID/g" {} +`
5. Create a private ECR repository for the "jenkins-master" image:

    ```bash
    aws ecr create-repository --repository-name jenkins-master --image-scanning-configuration scanOnPush=false --region $AWS_REGION
    ```

6. Manually build the Jenkins master image and upload it to ECR:

    ```bash
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com ; \
    docker tag jenkins-master:latest $ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/jenkins-master:latest ; \
    docker push $ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/jenkins-master:latest ;
    ```

7. List the Jenkins-master image in your ECR repository:

    ```bash
    aws ecr list-images --repository-name jenkins-master --region $AWS_REGION --output table
    ```

#### 4.1.2 Provision AWS Resources

Follow the steps below to install and configure the DevSecOps Jenkins scanner:

1. Copy the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` into the Cloud9 environment and set the environment variables:

    `curl ifconfig.io` get your local IP address

    ```bash
    export AWS_PAGER= ;\
    export AWS_REGION=ap-southeast-1 ;\
    export ACCOUNT=$(aws sts get-caller-identity --out json --query 'Account' | sed 's/"//g') ;\
    export CDK_DEFAULT_ACCOUNT=$ACCOUNT ;\
    export CDK_DEFAULT_REGION=$AWS_REGION ;\
    export CURRENT_IP=$YOURIP ;\
    echo -e "$ACCOUNT \\n$CURRENT_IP" ;
    ```
    
2. Initialize the CDK Toolkit:
    
    install the package 

    `pip install aws-cdk-lib constructs`

    ```bash
    cd cdk-jenkins
    cdk bootstrap aws://$ACCOUNT/$AWS_REGION
    ```

3. Use cloudformation list command to check the `CDKToolkit` exist

    `aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE --query "StackSummaries[].[StackName,StackStatus]" --output table`


4. Deploy the stack using CDK:
    
    ```bash
    cdk synth --context-json '{"branch_or_ref": "main"}' --context current_ip=$CURRENT_IP
    cdk deploy --context-json '{"branch_or_ref": "main"}' --context current_ip=$CURRENT_IP --require-approval never --all
    #cdk deploy --context-json '{"branch_or_ref": "main"}' --context current_ip=$CURRENT_IP --all #with confirmation
    ```

    |  Stack  |Time   |
    |----|---|
    | Network stack |157s   |
    | Jenkins Master Stack   | 317s  |
    | WebGoat Stack   | 191s   |
    | CodeBuild Stack | 71s |


5. Capture the `JenkinsMasterStack.LoadBalancerDNSName` output to access the Jenkins Master server


### 4.2 Jenkins Master

#### 4.2.1 Folder Layout

```
jenkins-master-image
├── Dockerfile - Docker file of Jenkins Master
├── Jenkinsfile - groovy script of pipeline
│   ├── codebuild-webgoat
│   ├── gauntlt-webgoat
│   └── pipelinejob
├── createJobs.groovy - the seed job to provision the pipeline in Jenkins file
├── plugins.txt - the plugin will be installed in Jenkins Master
└── seedJob.xml - Basic setup and create the seedjob
```

#### 4.2.2 Jenkins in CDK

```py
        cluster = ecs.Cluster(
            self, "jenkins-cluster", vpc=vpc, cluster_name="jenkins-cluster"
        )

        file_system = efs.FileSystem(
            self, "JenkinsFileSystem", vpc=vpc, removal_policy=RemovalPolicy.DESTROY
        )

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

        ecr_repository = ecr.Repository.from_repository_name(
            self, "jenkins-master", "jenkins-master")

        container_definition = task_definition.add_container(
            "jenkins",
            #image=ecs.ContainerImage.from_registry("jenkins/jenkins:lts"),
            image = ecs.ContainerImage.from_ecr_repository(ecr_repository, tag="latest"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="jenkins"),
        )
```

## 5 Jenkins pipleine overview

![](./docs/image/pipeline_flow.drawio.png)

1. access the Jenkins using NLB dns name

![](./docs/image/jenkins_main_page.png)

2. Execute the seed-job to provision the pipeline in Jenkins.
3. Execute `AWS_CodeBuild_webgoat` pipeline

![](./docs/image/jenkins_execution_error.png)

4. update the codebuild name in parameter/configure/groovy 

![](./docs/image/codebuild_output.png)

![](./docs/image/jenkins_paramater.png)

### 5.1 CodeBuild Deep dive

#### 5.1.1 Build spce

```yaml
version: 0.2

phases:
  install:
    commands:
      - nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://127.0.0.1:2375 --storage-driver=overlay2 &
      - timeout 15 sh -c "until docker info; do echo .; sleep 1; done"
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
      - aws --version
      - pwd && ls -lR
  build:
    commands:
      - echo Build started on `date`
      - echo Running your command in Docker...
      - docker pull $ECR_URL:latest
      - |
        docker run \
          --rm \
          -e APP_URL=$APP_URL \
          -e PYTHONPATH=/app/behave/libs \
          -v $(pwd):/app \
          $ECR_URL:latest \
          behave /app/behave/features | tee output.txt
      - echo "Command output:"
      - cat output.txt
  post_build:
    commands:
      - echo Build completed on `date`
```

#### 5.1.2 codebuild in CDK

```py
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
                compute_type=codebuild.ComputeType.SMALL,
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
```

### 5.2 Behave Tese Case 

```
Feature: Evaluate response header for a specific endpoint.

  Background: Set endpoint and base URL
    Given I am using the endpoint "$APP_URL"
    And I set base URL to "/"

  @runner.continue_after_failed_step
  Scenario: Check response headers
    Given a set of specific headers:
      | key                       | value                    |
      | Strict-Transport-Security | max-age=31536000; includeSubDomains |
      | Strict-Transport-Security | max-age=31536000; includeSubDomains; preload |
      | Content-Security-Policy   | default-src 'self'; script-src 'self'; object-src 'none'; style-src 'self'; base-uri 'none'; frame-ancestors 'none' |
      | X-Content-Type-Options    | nosniff |
      | X-Frame-Options           | SAMEORIGIN |
      | X-Frame-Options           | DENY |
      | Cache-Control             | no-cache |

    When I make a GET request to "WebGoat"
    Then the value of header "Cache-Control" should contain the defined value in the given set
    #And the the value of header "Strict-Transport-Security" should be in the given set
    #And the value of header "Content-Security-Policy" should be in the given set
    #And the value of header "X-Content-Type-Options" should be in the given set
    #And the value of header "X-Frame-Options" should be in the given set
```

#### 5.2.1 OTP demo using Behave


### Challenge

1. Update your CodeBuild name in the Groovy script and reflect the changes in the Jenkins Master.
    - update the codebuild
    - update createJobs.groovy to your repo
2. Collect the CodeBuild logs and display them in Jenkins.

## Clean up Action

To perform a clean action, follow these steps:

1. Destroy the provisioned resources.

    `cdk destroy --all`
2. Manual clean up ECR and S3
3. Check the Log group for any remaining logs.
4. check you bill in next day

## Reference

- [AWS Jenkins ECS CDK Sample](https://github.com/aws-samples/aws-jenkins-ecs-cdk)
- [Deploy your own production-ready Jenkins in AWS ECS](https://jenkinshero.com/deploy-jenkins-into-aws-ecs/)
- [Deploying Jenkins into AWS ECS using CDK](https://jenkinshero.com/deploying-jenkins-into-aws-ecs-using-cdk/)
- [DevOps with serverless Jenkins and AWS Cloud Development Kit (AWS CDK) | Amazon Web Services](https://aws.amazon.com/blogs/devops/devops-with-serverless-jenkins-and-aws-cloud-development-kit-aws-cdk/)
- [Setting up a CI/CD pipeline by integrating Jenkins with AWS CodeBuild and AWS CodeDeploy | Amazon Web Services](https://aws.amazon.com/blogs/devops/setting-up-a-ci-cd-pipeline-by-integrating-jenkins-with-aws-codebuild-and-aws-codedeploy/)
- [Integrating AWS CodeBuild into Jenkins pipelines](https://jenkinshero.com/integrating-aws-codebuild-into-jenkins-pipelines/)
- [Environments - AWS Cloud Development Kit (AWS CDK) v2](https://docs.aws.amazon.com/cdk/v2/guide/environments.html)
- [AWS CDK Toolkit (cdk command) - AWS Cloud Development Kit (AWS CDK) v2](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-config)

