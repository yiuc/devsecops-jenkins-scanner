#!/bin/bash

curl -iL http://webgoat.svc.test.local:8080/WebGoat 
gauntlt --tags @webgoat
#gauntlt --tags @final
