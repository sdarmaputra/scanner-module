import os
import sys
import git
import json
import helper
from shutil import copyfile
from docker import Client

printLog = helper.printLog
protocol = "http://"
agentList = {
		0: {'name': 'w3af0', 'address': '10.151.38.150:5000', 'running': 0, 'w3afPort': '5000', 'supervisorPort': '9000'},
		1: {'name': 'w3af1', 'address': '10.151.38.150:5001', 'running': 0, 'w3afPort': '5001', 'supervisorPort': '9001'},
		2: {'name': 'w3af2', 'address': '10.151.38.150:5002', 'running': 0, 'w3afPort': '5002', 'supervisorPort': '9002'},
		3: {'name': 'w3af3', 'address': '10.151.38.150:5003', 'running': 0, 'w3afPort': '5003', 'supervisorPort': '9003'},
	}

docker_client = Client(base_url = 'unix://var/run/docker.sock')

# Create new docker container
def createAgentContainer(app_name, w3af_port, supervisor_port):
	printLog("-------Starting Container Creator Activities!-------")
	# Create docker container for application sandbox
	new_container = docker_client.create_container(image = "andresriancho/w3af-api", 
		name = app_name,
		ports = [5000, 9001],
		host_config = docker_client.create_host_config(
			port_bindings = {5000 : w3af_port, 9001: supervisor_port}
	    )
	)
	printLog("Docker creates:", new_container, " on port ", w3af_port)
	return

def checkAgentAvailability():
	containers = docker_client.containers(all=True)
	for key, agent in agentList.iteritems():
		if not any(container['Names'][0] == ('/' + agent['name']) for container in containers):
			createAgentContainer(agent['name'], agent['w3afPort'], agent['supervisorPort'])
	return

def stopAllAgent():
	for key, agent in agentList.iteritems():
		printLog('Stoping agent', agent['name'], '@', agent['address'])
		docker_client.stop(agent['name'])
		agent['running'] = 0
	return

def stopByAddress(address):
	counter = 0
	for key, agent in agentList.iteritems():
		if (agent['address'] == address):
			printLog('Stoping agent', agent['name'], '@', agent['address'])
			docker_client.stop(agent['name'])
			agent['running'] = 0
			return {'status': 'success', 'address': agent['address'], 'state': 'stopped'}
		counter += 1
	if (counter == len(agentList)):
		printLog('No agent with specified address!')
		return {'status': 'failed', 'message': 'No agent with specified address!'}

def startAgent():
	counter = 0
	for key, agent in agentList.iteritems():
		if (agent['running'] == 0):
			printLog('Starting agent', agent['name'], '@', agent['address'])
			docker_client.start(agent['name'])
			agent['running'] = 1
			printLog('Successfully running agent', agent['name'], '@', agent['address'])
			return {'status': 'success', 'address': protocol+agent['address']}
		counter += 1
	if (counter == len(agentList)):
		printLog('All agent in use. Can not start new task!')
		return {'status': 'failed', 'message': 'All agent in use. Can not start new task!'}

def main():
	print "Please use this program as plug-in. Thanks!"

if __name__ == "__main__":
	main()