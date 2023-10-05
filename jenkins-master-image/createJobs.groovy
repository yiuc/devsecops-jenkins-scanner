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
pipelineJob('AWS CodeBuild webgoat') {
    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url 'https://github.com/yiuc/devsecops-jenkins-scanner.git'
                    }
                    branch 'main'
                    scriptPath('jenkins-master-image/Jenkinsfile/codebuild-webgoat')
                }
            }
        }
    }
}
pipelineJob('pipelineJob') {
    definition {
        cps {
            script(readFileFromWorkspace('jenkins-master-image/Jenkinsfile/pipelineJob'))
            sandbox()
        }
    }
}