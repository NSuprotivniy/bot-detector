import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.web import StaticFileHandler
import time
import pickle
import base64
import copy
import json
import os
import shutil
import psutil
import zipfile

# our methods
import methods

define("port", default=12121, help="run on the given port", type=int)

TEMPLATES_DIR = "templates"
DATA_DIR = "data"
MODELS_DIR = "models"
GRAPH_DIR = "graph"
		
curModel = None
curData = ""
curName = ""
		
def modelPredict(methodType, dataFile, name, query):
	global curModel, curData, curName
	if not curModel or curData != dataFile or curName != name:
		curModel = methods.methodsMap[methodType]
		curModel.loadData(dataFile, -1)
		curModel.loadModel(name) # load model and traing labels for encoder
		curData = dataFile
		curName = name
		print("Loaded")	
	data = curModel.predict(query)
	return(json.dumps(data))
		
def testMethod(methodType, dataFile, sampleSize):
	testMethod = methods.methodsMap[methodType]
	testMethod.loadData(dataFile, sampleSize)
	data = testMethod.test()
	return json.dumps(data)
		
def trainModel(methodType, dataFile, sampleSize, name):
	trainingModel = methods.methodsMap[methodType]
	trainingModel = methods.HeadersModel()
	trainingModel.loadData(dataFile, sampleSize)
	trainingModel.train()
	data = trainingModel.saveModel(name)
	return json.dumps(data)
		

executor = ThreadPoolExecutor(max_workers=8)
		
class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", IndexHandler),
			(r"/upload", UploadHandler),
			(r"/deletedata", DeleteDataHandler),
			(r"/testmethod", MethodTestHandler),
			(r"/trainmodel", ModelTrainHandler),
			(r"/deletemodel", DeleteModelHandler),
			(r"/predict", ModelPredictHandler),
			(r"/sysstats", SysStatsHandler),
			(r"/(.*.css)", StaticFileHandler, {"path": "./templates/"},),
			(r"/(.*.js)", StaticFileHandler, {"path": "./templates/"},),
		]
		tornado.web.Application.__init__(self, handlers)

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		files = os.listdir("data")
		models = os.listdir(os.path.join("models", "headers"))
		self.render("templates/index.html", files=files, models=models)

class UploadHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		original_fname = self.file1['filename']
		extension = os.path.splitext(original_fname)[1]
		if extension not in  [".parquet", ".csv", ".zip"]:
			self.set_status(300)
			return
		if os.path.exists(os.path.join(DATA_DIR, original_fname)):
			self.set_status(201)
		output_file = open(os.path.join(DATA_DIR, original_fname), 'wb')
		output_file.write(self.file1['body'])
		output_file.close()
		if extension == ".zip":
			zip_ref = zipfile.ZipFile(os.path.join(DATA_DIR, original_fname), 'r')
			zip_ref.extractall(DATA_DIR)
			zip_ref.close()
			os.remove(os.path.join(DATA_DIR, original_fname))
			original_fname = os.path.splitext(original_fname)[0]
		data = {}
		data['name'] = original_fname
		jsonData = json.dumps(data)
		return jsonData
		
	@tornado.gen.coroutine
	def post(self):
		self.file1 = self.request.files['data'][0]
		res = yield self.start_worker()
		self.finish(res)
		
		
		
class DeleteDataHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		name = self.params["name"]
		try:
			if os.path.isdir(os.path.join(DATA_DIR, name)):
				shutil.rmtree(os.path.join(DATA_DIR, name))
			else:
				os.remove(os.path.join(DATA_DIR, name))
			self.set_status(200)
			return
		except:
			self.set_status(404)
			return
		
	@tornado.gen.coroutine
	def delete(self):
		self.params = json.loads(self.request.body.decode("utf-8"))
		self.start_worker()
		self.finish()
			
class DeleteModelHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		name = self.params["name"]
		modelType = None
		if int(self.params["method"]) == 1:
			modelType = "headers"
		try:
			os.remove(os.path.join(MODELS_DIR, modelType, name))
			self.set_status(200)
			return
		except:
			self.set_status(404)
			return

	@tornado.gen.coroutine
	def delete(self):
		self.params = json.loads(self.request.body.decode("utf-8"))
		self.start_worker()
		self.finish()
		
			
class MethodTestHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		print(self.params)
		jsonData = testMethod(int(self.params["method"]), self.params["data"], int(self.params["sampleSize"]))
		return jsonData

	@tornado.gen.coroutine
	def post(self):
		self.params = json.loads(self.request.body.decode("utf-8"))
		res = yield self.start_worker()
		self.finish(res)
		
class ModelTrainHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		print(self.params)
		name = self.params["name"]
		if int(self.params["method"]) == 1:
			modelType = "headers"
			extension = "hdr"
		if(os.path.isfile(os.path.join(MODELS_DIR, modelType, name+"."+extension))):
			self.set_status(201)
		jsonData = trainModel(int(self.params["method"]), self.params["data"], int(self.params["sampleSize"]), name)
		return jsonData

	@tornado.gen.coroutine
	def post(self):
		self.params = json.loads(self.request.body.decode("utf-8"))
		res = yield self.start_worker()
		self.finish(res)
		
class ModelPredictHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		jsonData = modelPredict(self.params["method"], self.params["data"], self.params["name"], self.params["query"])
		return jsonData

	@tornado.gen.coroutine
	def post(self):
		self.params = json.loads(self.request.body.decode("utf-8"))
		res = yield self.start_worker()
		self.finish(res)
		
class SysStatsHandler(tornado.web.RequestHandler):
	executor = executor
	@run_on_executor
	def start_worker(self):
		data = {}
		data["CPU usage"] = psutil.cpu_percent(interval=1)
		data["memory usage"] = psutil.virtual_memory().percent
		data["swap usage"] = psutil.swap_memory().percent
		jsonData = json.dumps(data)
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
	main()