import os
import time
from w3af_api_client import Connection, Scan
import helper
from pprint import pprint

printLog = helper.printLog
parent_dir = '/home/jiwa/tugasakhir/'

def initConnection(scannerUrl):
	printLog("Initialize connection with scanner at ", scannerUrl)
	conn = Connection(scannerUrl)
	printLog("Version: ", conn.get_version())
	return conn

def startScanner(conn, targetUrl):
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
	
	while True:
		status = scan.get_status()
		print "Running Status:", status['is_running']
		if (status['is_running'] == False):
			break
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

def initTask(scannerUrl, targetUrl):
	conn = initConnection(scannerUrl)
	result = startScanner(conn, targetUrl)
	return result

def main():
	print "Please use this program as plug-in. Thanks!"

if __name__ == "__main__":
	main()

