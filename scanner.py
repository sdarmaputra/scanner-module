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
	def __init__(self, scenarioId, applicationName, conn, scannerUrl, targetUrl, scan):
		printLog("Thread for", applicationName, "created")
		threading.Thread.__init__(self)
		self.scenarioId = scenarioId
		self.name = applicationName
		self.conn = conn
		self.targetUrl = targetUrl
		self.scannerUrl = scannerUrl
		self.scan = scan
		print "scanner", self.scannerUrl

	def run(self):
		postUrl = "http://10.151.36.30:3000/runner/run/"+self.scenarioId
		printLog("Running thread task")
		results = retrieveResults(self.conn, self.targetUrl, self.scan)
		
		req = requests.post(postUrl, data={'results': json.dumps(results['results'])})
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
		conn = Connection(scannerUrl)
		printLog("Version: ", conn.get_version())
		return conn

	def startScanner(self, scenarioId, applicationName, conn, scannerUrl, targetUrl):
		scan = Scan(conn)
		scanProfilePath = os.path.join(parent_dir, "w3af/profiles/OWASP_TOP10.pw3af")
		scanProfile = file(scanProfilePath).read()
		targetUrls = [targetUrl]

		print scanProfile

		printLog("")
		printLog("Starting scanner for target ", targetUrl)
		scan.start(scanProfile, targetUrls)

		time.sleep(10)
		scan.get_urls()
		scan.get_log()
		time.sleep(3)

		retrieverThread = ResultRetriever(scenarioId, applicationName, conn, scannerUrl, targetUrl, scan)
		retrieverThread.start()
		
		return {'status': "success", 'state': "running"}

	def initTask(self, scenarioId, applicationName, scannerUrl, targetUrl):
		conn = self.initConnection(scannerUrl)
		result = self.startScanner(scenarioId, applicationName, conn, scannerUrl, targetUrl)		
		return result


def retrieveResults(conn, targetUrl, scan):
	printLog("Start retrieving results for target ", targetUrl)
	while True:
		try:
			status = scan.get_status()
			print "Running Status:", status['is_running'], "for target:", targetUrl
			if (status['is_running'] == False):
				break
		except Exception as e:
			print "Target ", targetUrl, "error occured: ", e
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

