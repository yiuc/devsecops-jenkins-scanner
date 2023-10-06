#!/bin/bash

curl -s -o /dev/null -L -v http://webgoat.svc.test.local:8080/WebGoat
gauntlt --tags @webgoat
#gauntlt --tags @reallyslow
#gauntlt --tags @final
