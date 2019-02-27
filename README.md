# ec2-lambda-events
A python script for automatically handling AWS EC2 maintenance events


Most of the good README stuff can be found in comments inline of the code. 



TO DO: 

Handle multiple instance events at the same time, at currently it's single threaded and will choke if you have multiple pending events as the list building/comprehension logic hasn't been built. 

Slack notifications 
