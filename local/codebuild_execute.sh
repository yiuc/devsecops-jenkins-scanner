# execute the codebuild
# find the build id and log stream name
# tail the logs

PROJECT_NAME=$1 && 
BUILD_ID=$(aws codebuild start-build --project-name $PROJECT_NAME --query 'build.id' --output text); sleep 1 && 
LOG_STREAM=$(aws codebuild batch-get-builds --ids $BUILD_ID --query 'builds[0].logs.streamName' --output text); sleep 1 && 
LOG_GROUP_NAME="/aws/codebuild/$PROJECT_NAME"; sleep 1 && 
aws logs tail $LOG_GROUP_NAME --log-stream-names $LOG_STREAM --follow