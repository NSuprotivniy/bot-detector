import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.web import StaticFileHandler
import json
import os
import sys
from time import time

# our methods
import methods

from sklearn.base import TransformerMixin

class HashingTrick(TransformerMixin):
	_default_hashing_trick_modulars = {
		'DeviceClass': 10000,
		'DeviceName': 10000,
		'DeviceBrand': 10000,
		'DeviceCpu': 10000,
		'DeviceCpuBits': 10000,
		'OperatingSystemClass': 10000,
		'OperatingSystemName': 10000,
		'OperatingSystemVersion': 10000,
		'OperatingSystemNameVersion': 10000,
		'OperatingSystemVersionBuild': 10000,
		'LayoutEngineClass': 10000,
		'LayoutEngineName': 10000,
		'LayoutEngineVersion': 10000,
		'LayoutEngineVersionMajor': 10000,
		'LayoutEngineNameVersion': 10000,
		'LayoutEngineNameVersionMajor': 10000,
		'AgentClass': 10000,
		'AgentName': 10000,
		'AgentVersion': 10000,
		'AgentVersionMajor': 10000,
		'AgentNameVersion': 10000,
		'AgentNameVersionMajor': 10000,
		'from': 10000,
		'to': 10000,
		'url': 10000000,
		'requestType': 10000,
		'operation': 10000
	}
	
	FEATURES = [
	'DeviceClass',
	'DeviceName',
	'DeviceBrand',
	'DeviceCpu',
	'DeviceCpuBits',
	'OperatingSystemClass',
	'OperatingSystemName',
	'OperatingSystemVersion',
	'OperatingSystemNameVersion',
	'OperatingSystemVersionBuild',
	'LayoutEngineClass',
	'LayoutEngineName',
	'LayoutEngineVersion',
	'LayoutEngineVersionMajor',
	'LayoutEngineNameVersion',
	'LayoutEngineNameVersionMajor',
	'AgentClass',
	'AgentName',
	'AgentVersion',
	'AgentVersionMajor',
	'AgentNameVersion',
	'AgentNameVersionMajor',
	#     'from',
	#     'to',
	#     'url',
	#     'requestType',
	'operation'
	]

	def __init__(self, hashing_trick_modulars = _default_hashing_trick_modulars):
		self.hashing_trick_modulars = hashing_trick_modulars

	def set_params(self, **kwargs):
		"""Set the parameters of this estimator."""

	def get_params(self, **kwargs):
		return {"hashing_trick_modulars": self.hashing_trick_modulars}
		
	def _hashing_trick(self, x, n):
		return hash(x) % n

	def _column_hashing_trick(self, col_name):
		self.http[col_name] = self.http[col_name].apply(self._hashing_trick, args=(self.hashing_trick_modulars[col_name],))

	def fit_transform(self, X, *_):
		return self.transform(X)
		
	def transform(self, X, *_):
		self.http = X
		for feature in self.FEATURES:
			self._column_hashing_trick(feature)

		return self.http

	def fit(self, *_):
		return self

define("port", default=8080, help="run on the given port", type=int)

model = None
predicts_list = []
		
def modelPredict(methodType, query):
	predicts_list.append(model.predict(query))
	return(json.dumps({'result' : 'success' }))	

executor = ThreadPoolExecutor(max_workers=8)
		
class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", IndexHandler),
			(r"/predict", ModelPredictHandler),
			(r"/results", GetResultsHandler),
			(r"/(.*.css)", StaticFileHandler, {"path": "./templates/"},),
			(r"/(.*.js)", StaticFileHandler, {"path": "./templates/"},),
		]
		tornado.web.Application.__init__(self, handlers)

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("templates/index.html", files=[], models=[])

class ModelPredictHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		jsonData = modelPredict('headers', self.params)
		return jsonData

	@tornado.gen.coroutine
	def post(self):
		self.params = json.loads(self.request.body.decode("utf-8"))
		res = yield self.start_worker()
		self.finish(res)
		
class GetResultsHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		global predicts_list
		bots_num = 5
		users_num = 1
		for predict in predicts_list:
			if predict['proba'] < 0.5:
				users_num = users_num + 1
			else:
				bots_num = bots_num + 1
		data = { 'users' : users_num , 'bots' : bots_num }
		jsonData = json.dumps(data)
		predicts_list = []
		return jsonData

	@tornado.gen.coroutine
	def get(self):
		res = yield self.start_worker()
		self.finish(res)

def main():
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	try:
		pickle_path = sys.argv[1]
	except:
		print("Enter path to the saved model files!")
		exit(-1)
	model = methods.methodsMap['headers']
	model.loadModel(pickle_path)
	print("Model loaded...")
	model.start_time = time()
	main()