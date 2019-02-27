import boto3
import time
import sys
from retrying import retry


ec = boto3.client('ec2')

reservations = ec.describe_instance_status(
        Filters=[     
             {
            'Name': 'event.code',
            'Values': [
                '*',
            ]
        },
     ],
  )

try:
	# Use this if you want to test on a single instance 
	#maintenenaceids = ('instance-id')
	maintenenaceids = reservations['InstanceStatuses'][0]["InstanceId"]
	print('%s is scheduled for maintenenace\n' %(maintenenaceids))
except IndexError:
	maintenenaceids = ('')
	print('Nothing scheduled for maintenance exiting')
	sys.exit() 



# Function for stopping the mainteanceids instances

def instance_stop (id):
 ec.stop_instances(
    InstanceIds=[
        (maintenenaceids),
    ],
  
)

# Function for starting the instance if it's not in an ASG otherwise you'll get an error about the instance not being in a state "from which it can't be started. (IndexError)" 

@retry(stop_max_attempt_number=10, wait_fixed=10000)
def instance_start (id):
 ec.start_instances(
    InstanceIds=[
        (maintenenaceids),
    ],
  
)
 sys.exit()


# Describe the instance status code to determine if we can actually start it in it's current state 

def instance_describe (id):
	instance_state = ec.describe_instance_status(
        Filters=[     
             {
            'Name': 'instance-state-name',
            'Values': [
                'stopped',
            ]
        },
     ],
     InstanceIds=[
        (maintenenaceids),
        ],
     IncludeAllInstances=True

  )
	try:
		instance_code = (instance_state["InstanceStatuses"][0]["InstanceState"]['Code'])
	except IndexError:
		instance_code = []

	# while the return code does not equal 80 aka the "ready to start" RC then we'll just sleep a while and try again.

	while instance_code != 80: 	 
  		print "Not ready to start"
  		time.sleep(15)
  		instance_describe(maintenenaceids)
  		
	else: 
  		print("We're safe to start! Starting %s" %(maintenenaceids))
  		instance_start(maintenenaceids)

# Check if the maintenenaceids instance contains the "aws:autoscaling:groupName" tag, if so we notify and take no automated action. else we stop and start it. 

def asg_instance_stop (id):

	ec2 = boto3.resource('ec2')
	ec2instance = ec2.Instance(maintenenaceids)
	instancename = ''
	for tags in ec2instance.tags:
		if tags["Key"] == 'aws:autoscaling:groupName':
		 instancename = tags["Value"]
		 print("The ASG tag exists, we'll stop the instance and let ASG take over ASG NAME %s" %(instancename))
		 instance_stop(maintenenaceids)
		 break
	
 	else:	
			print("The ASG tag does not exist, we'll stop and start the instance %s" %(instancename))
			instance_stop(maintenenaceids)
			instance_describe(maintenenaceids)

    	
# Need logic here for particular "stateful" tag which we will not stop an instance if exists

try:
 	asg_instance_stop(maintenenaceids)

except:
	print "Somethigns wrong, exiting" 
	sys.exit()
	



