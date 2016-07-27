import os
import time
from w3af_api_client import Connection, Scan
import helper
from pprint import pprint
import threading
import requests
import json
import agentRunner

printLog = helper.printLog
parent_dir = '/home/jiwa/tugasakhir/'

class ResultRetriever(threading.Thread):
	def __init__(self, scenarioId, applicationName, runningToken, conn, scannerUrl, targetUrl, scan):
		printLog("Thread for", applicationName, "created")
		threading.Thread.__init__(self)
		self.scenarioId = scenarioId
		self.name = applicationName
		self.runningToken = runningToken
		self.conn = conn
		self.targetUrl = targetUrl
		self.scannerUrl = scannerUrl
		self.scan = scan

	def run(self):
		postUrl = "http://10.151.36.30:3000/runner/storeResult/"+self.scenarioId
		printLog("Running thread task")
		results = retrieveResults(self.conn, self.targetUrl, self.scan)

		payloads = {
			'applicationName': self.name,
			'scenarioId': self.scenarioId,
			'targetUrl': self.targetUrl,
			'scannerUrl': self.scannerUrl,
			'runningToken': self.runningToken,
			'results': json.dumps(results['results'])
		}
		
		req = requests.post(postUrl, data=payloads)
		printLog(req.text)
		printLog(req.status_code)

		res = agentRunner.stopByAddress(self.scannerUrl)
		
		printLog(res)
		printLog("thread finished")

class Scanner(object):
	def __init__(self):
		printLog("Scanner object created")

	def initConnection(self, scannerUrl):
		printLog("Initialize connection with scanner at ", scannerUrl)
		
		while True:
			try:
				printLog("Trying initialization for scanner:", scannerUrl)
				conn = Connection(scannerUrl)
				ver = conn.get_version()
				if (ver is not None):
					printLog("Version: ", conn.get_version())
					printLog("Scanner initialized: ", scannerUrl)
					break
				else:
					pass
			except Exception, e:
				pass
			else:
				pass
			finally:
				pass
			time.sleep(3)		
		
		return conn

	def startScanner(self, scenarioId, applicationName, runningToken, conn, scannerUrl, targetUrl):
		scanProfilePath = os.path.join(parent_dir, "w3af/profiles/OWASP_TOP10.pw3af")
		scanProfile = file(scanProfilePath).read()
		targetUrls = [targetUrl]

		printLog("Starting scanner for target ", targetUrl)
		scan = Scan(conn)
		try:
			scan.start(scanProfile, targetUrls)
		except Exception, e:
			printLog("Error while starting scanner for target", targetUrl, ":", e)
		else:
			pass
		finally:
			pass

		printLog("Checking status for target", targetUrl)
		while True:
			try:
				stat = scan.get_status()
				printLog("Stat for target", targetUrl, ":", stat)
				if stat is not None:
					break
				
			except Exception, e:
				printLog("Stat for target", targetUrl, ":", e)
				pass
			time.sleep(3)
		

		# Check if scanner has running
		printLog("Checking running status for", targetUrl)
		while True:
			try:
				status = scan.get_status()
				printLog("Running Status:", status['is_running'], "for target:", targetUrl)
				if (status['is_running'] == True):
					printLog("scan started for target: ", targetUrl)
					break
				else:
					pass
			except Exception as e:
				printLog("Target ", targetUrl, "error occured: ", e)
				pass
			else:
				pass
			finally:
				pass
			time.sleep(3)

		printLog("starting thread for", targetUrl)
		retrieverThread = ResultRetriever(scenarioId, applicationName, runningToken, conn, scannerUrl, targetUrl, scan)

		# Check if thread has been started
		while True:
			try:
				printLog("trying to start thread for", targetUrl)
				retrieverThread.start()
				printLog("thread for target", targetUrl, " live status: ", retrieverThread.isAlive())
				if not retrieverThread.isAlive():
					pass			
				else:
					break;
			except Exception, e:
				pass
			else:
				pass
			finally:
				pass
			time.sleep(3)

		
		return {'status': "success", 'state': "running", 'token': runningToken, 'scenarioId':scenarioId, 'applicationName': applicationName}

	def initTask(self, scenarioId, applicationName, runningToken, scannerUrl, targetUrl):
		conn = self.initConnection(scannerUrl)
		result = self.startScanner(scenarioId, applicationName, runningToken, conn, scannerUrl, targetUrl)		
		return result


def retrieveResults(conn, targetUrl, scan):
	printLog("Start retrieving results for target ", targetUrl)
	while True:
		try:
			status = scan.get_status()
			printLog("Running Status:", status['is_running'], "for target:", targetUrl)
			if (status['is_running'] == False):
				break
		except Exception as e:
			printLog("Target ", targetUrl, "error occured: ", e)
			pass
		time.sleep(3)

	summary = scan.get_findings()
	finalResult = {'results': {}}

	for index in range(len(summary)):
		currentSummary = summary[index].resource_data
		tmp_result = { index: {
				'targetUrl': currentSummary['url'],
				'vulnerability': currentSummary['name'],
				'longDescription': currentSummary['long_description'],
				'description': currentSummary['desc'],
				'severity': currentSummary['severity'],
				'recommendation': currentSummary['fix_guidance'],
				'references': currentSummary['references']
			}}
		if 'urls' in currentSummary:
			tmp_result['targetUrls'] = currentSummary['urls']
		finalResult['results'].update(tmp_result)
	return finalResult

def main():
	print "Please use this program as plug-in. Thanks!"

if __name__ == "__main__":
	main()

