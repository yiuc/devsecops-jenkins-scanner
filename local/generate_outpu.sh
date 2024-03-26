#!/bin/bash

# that is the function to update the codebuild id 
cd cdk-jenkins
output=$(aws cloudformation describe-stacks \
--stack-name CodeBuildStack \
--query "Stacks[].Outputs[]" \
--output json | \
jq --arg stack CodeBuildStack -r '.[] |
"\(.OutputKey)=\(.OutputValue | @sh)"')

while read -r line; do
    # Split the line by '=' and capture the key and value
    key=$(echo "$line" | cut -d'=' -f1)
    value=$(echo "$line" | cut -d'=' -f2)

    # Assign the value to a variable with the key as the variable name
    #declare "${key}=${value}"
    sed -i "s/%$key/$value/g" ../jenkins-master-image/Jenkinsfile/*
done <<< "$output"