#!/bin/sh

aws ec2 describe-instances --filters "Name=image-id,Values=$AMI" "Name=instance-state-name,Values=pending,running" | grep INSTANCES | awk {'print $8'}
