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
		0: {'name': 'w3af0', 'address': '10.151.36.92:5000', 'running': 0},
		1: {'name': 'w3af1', 'address': '10.151.36.92:5001', 'running': 0},
		2: {'name': 'w3af2', 'address': '10.151.36.92:5002', 'running': 0},
		3: {'name': 'w3af3', 'address': '10.151.36.92:5003', 'running': 0},
	}

docker_client = Client(base_url = 'unix://var/run/docker.sock')

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