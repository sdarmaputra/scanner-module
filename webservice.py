import tornado.ioloop
import tornado.web
from tornado import gen
from cStringIO import StringIO
from multiprocessing.pool import ThreadPool
import sys
import helper
import agentRunner
from scanner import Scanner

printLog = helper.printLog
_workers = ThreadPool(10)

def runBackground(function, callback, args=(), kwds={}):
	def _callback(result):
		tornado.ioloop.IOLoop.instance().add_callback(lambda: callback(result))
	_workers.apply_async(function, args, kwds, _callback)

class Runner(tornado.web.RequestHandler):
	def get(self, *args, **argv):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header("Access-Control-Allow-Methods", "POST, GET")
		if (args[0] == None):
			res = agentRunner.startAgent()
			self.write(res)
		else:
			self.write(args[0])

	def delete(self, *args, **argv):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header("Access-Control-Allow-Methods", "POST, GET")
		if (args[0] != None):
			res = agentRunner.stopByAddress(args[0])
			self.write(res)

class ScannerAgent(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self, *args, **argv):
		scenarioId = self.get_argument("scenario_id")
		applicationName = self.get_argument("application_name")
		runningToken = self.get_argument("running_token")
		targetUrl = self.get_argument("target_url")
		scannerUrl = self.get_argument("scanner_url")

		currScanner = Scanner() 
		runBackground(currScanner.initTask, self.on_complete, (scenarioId, applicationName, runningToken, scannerUrl, targetUrl))

	def on_complete(self, res):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header("Access-Control-Allow-Methods", "POST, GET")
		self.write(res)
		self.finish()

def make_app():
	printLog("Application started")
	return tornado.web.Application([
		(r"/run/?([0-9.:]+)?", Runner),
		(r"/scan/?([0-9.:]+)?", ScannerAgent)
	])

if __name__ == "__main__":
	port = 8000
	agentRunner.checkAgentAvailability()
	agentRunner.stopAllAgent()
	agentRunner.checkAgentAvailability()
	application = make_app()
	application.listen(port)
	printLog('Listening on port ' + str(port))
	tornado.ioloop.IOLoop.current().start()
