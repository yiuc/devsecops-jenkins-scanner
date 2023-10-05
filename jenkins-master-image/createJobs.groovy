pipelineJob('AWS CodeBuild example using GitHub') {
    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url 'https://github.com/tkgregory/spring-boot-api-example.git'
                    }
                    branch 'simplified-for-ci'
                    scriptPath('Jenkinsfile-codebuild-github')
                }
            }
        }
    }
}
pipelineJob('AWS CodeBuild example using S3') {
    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url 'https://github.com/tkgregory/spring-boot-api-example.git'
                    }
                    branch 'simplified-for-ci'
                    scriptPath('Jenkinsfile-codebuild-s3')
                }
            }
        }
    }
}