#FROM jenkins/jenkins:2.277-jdk11
# https://abrahamntd.medium.com/automating-jenkins-setup-using-docker-and-jenkins-configuration-as-code-897e6640af9d
FROM jenkins/jenkins:lts

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

COPY seedJob.xml /usr/share/jenkins/ref/jobs/seed-job/config.xml

ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false