#!/bin/bash
python DockerRelaunch.py RLS
sleep 5
python DockerRelaunch.py BP
sleep 5
python DockerRelaunch.py XCAP
sleep 5
python DockerRelaunch.py WCSR
sleep 5
python DockerRelaunch.py POC
sleep 5
python DockerRelaunch.py MEDIA
