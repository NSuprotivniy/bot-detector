import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import time
import pickle
import base64
import copy
import json
import os
import shutil
import psutil
import zipfile

# ml dependencies
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import seaborn as sns
import user_agents
from matplotlib import pyplot as plt
pd.set_option("display.precision", 2)
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.tree import export_graphviz
from tornado.options import define, options
# ml dependencies

define("port", default=12121, help="run on the given port", type=int)

TEMPLATES_DIR = "templates"
DATA_DIR = "data"
MODELS_DIR = "models"
GRAPH_DIR = "graph"

encoders = []

def encode(col):
	le = LabelEncoder()
	le.fit(col)
	global encoders
	encoders.append(le.classes_)
	return le.transform(col)
	
def encodeReuse(col):
	le = LabelEncoder()
	global encoders
	le.classes_ = encoders.pop(0)
	return le.transform(col)
	
class baseModel():
	model = None
	modelType = "baseModel"
	type_file_extension = "bsm"
	def saveModel(self, name):
		filename = os.path.join(MODELS_DIR, self.modelType, name + "." + self.type_file_extension)
		pickle.dump(self.model, open(filename, 'wb'))
	def loadModel(self, name):
		filename = os.path.join(MODELS_DIR, self.modelType, name + "." + self.type_file_extension)
		self.model = pickle.load(open(filename, 'rb'))
	
class HeadersModel(baseModel):
	model = None
	dataset = None
	labels = None
	X = None
	y = None
	modelType = "headers"
	type_file_extension = "hdr"
	def loadData(self, dataFile, sampleSize):
		extension = os.path.splitext(dataFile)[1]
		if os.path.isdir(os.path.join(DATA_DIR, dataFile)) or extension == ".parquet":
			self.dataset = pq.read_table(os.path.join(DATA_DIR, dataFile)).to_pandas().head(sampleSize)
		elif extension == ".csv":
			self.dataset = pd.read_csv(os.path.join(DATA_DIR, dataFile)).head(sampleSize)
		self.X = self.dataset[[
			'userAgentIsBot',
			'userAgentIsMobile',
			'userAgentIsTablet',
			'userAgentIsTouchCapable',
			'userAgentIsPC',
			'userAgentOSFamily',
			'userAgentOSVersion0',
			'userAgentOSVersion1',
			'userAgentOSVersion2',
			'userAgentBrowserFamily',
			'userAgentBrowserVersion0',
			'userAgentBrowserVersion1',
			'userAgentBrowserVersion2',
			'userAgentDeviceFamily',
			'userAgentDeviceBrand',
			'userAgentDeviceModel',
			'from',
			'to',
			'url',
			'requestType',
			'operation'
		]].apply(encode, axis=0)
		self.labels = encoders
		self.y = self.dataset['isBot']
	def train(self):
		self.model = RandomForestClassifier(n_estimators=5, 
			max_depth = 19,  
			max_features = 15,
			n_jobs=-1, 
			random_state=17)
		self.model.fit(self.X, self.y)
	def predict(self, query):
		if query != "":
			predictDs = self.dataset.query(query)
		else:
			predictDs = self.dataset
		global encoders
		encoders = copy.deepcopy(self.labels)
		predictX = predictDs[[
			'userAgentIsBot',
			'userAgentIsMobile',
			'userAgentIsTablet',
			'userAgentIsTouchCapable',
			'userAgentIsPC',
			'userAgentOSFamily',
			'userAgentOSVersion0',
			'userAgentOSVersion1',
			'userAgentOSVersion2',
			'userAgentBrowserFamily',
			'userAgentBrowserVersion0',
			'userAgentBrowserVersion1',
			'userAgentBrowserVersion2',
			'userAgentDeviceFamily',
			'userAgentDeviceBrand',
			'userAgentDeviceModel',
			'from',
			'to',
			'url',
			'requestType',
			'operation'
		]].apply(encodeReuse, axis=0)
		proba_array = self.model.predict_proba(predictX)
		data = {}
		data["array"] = []
		proba_index = 0
		for index, row in predictDs.iterrows():
			entry = {}
			entry["userId"] = row['userId']
			entry["proba"] = proba_array[proba_index][1]
			data["array"].append(entry)
			proba_index = proba_index + 1
		return data
	def test(self):
		cv_scores, holdout_scores = [], []
		split = np.arange(0.1, 0.8, 0.1)
		for i in split:
			X_train, X_holdout, y_train, y_holdout = train_test_split(self.X, self.y, test_size=i, random_state=17)
			forest = RandomForestClassifier(n_estimators=5, 
											max_depth = 19,  
											max_features = 15,
											n_jobs=-1, 
											random_state=17)
			cv_scores.append(np.mean(cross_val_score(forest, X_train, y_train, cv=2, scoring='f1')))
			forest.fit(X_train, y_train)
			holdout_scores.append(f1_score(y_holdout, forest.predict(X_holdout)))
		plt.plot(split * self.X.shape[0], cv_scores, label='CV')
		plt.plot(split * self.X.shape[0], holdout_scores, label='holdout')
		plt.title('Forest test split')
		plt.legend()
		plt.savefig(os.path.join(GRAPH_DIR, 'result.png'), dpi=60)
		plt.close()
		with open(os.path.join(GRAPH_DIR, 'result.png'), "rb") as imageFile:
			imageBase64 = base64.b64encode(imageFile.read())
		data = {}
		data['html'] = "<img id=\"resultGraph\" src=\"\"/>";
		data['script'] = "function renderResult() {$(\"#resultGraph\").attr(\"src\",\"data:image/gif;base64,\"+rawImg1);}"
		data['rawImg1'] = imageBase64.decode("ascii")
		return data
	def saveModel(self, name):
		filename = os.path.join(MODELS_DIR, self.modelType, name + "." + self.type_file_extension)
		save = [self.model, self.labels]
		pickle.dump(save, open(filename, 'wb'))
	def loadModel(self, name):
		filename = os.path.join(MODELS_DIR, self.modelType, name)
		save = pickle.load(open(filename, 'rb'))
		self.model = save[0]
		self.labels = save[1]
		
curModel = None
curData = ""
curName = ""
		
def modelPredict(methodType, dataFile, name, query):
	if methodType == 1:
		global curModel, curData, curName
		if not curModel or curData != dataFile or curName != name:
			curData = dataFile
			curName = name
			curModel = HeadersModel()
			curModel.loadData(dataFile, -1)
			print("Loaded")
			curModel.loadModel(name) # load model and traing labels for encoder
		data = curModel.predict(query)
		return(json.dumps(data))
		
def testMethod(methodType, dataFile, sampleSize):
	if methodType == 1:
		headers = HeadersModel()
		headers.loadData(dataFile, sampleSize)
		data = headers.test()
		return json.dumps(data)
		
def trainModel(methodType, dataFile, sampleSize, name):
	if methodType == 1:
		headers = HeadersModel()
		headers.loadData(dataFile, sampleSize)
		headers.train()
		headers.saveModel(name)
		data = {}
		data['name'] = name + "." + headers.type_file_extension
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
			(r"/sysstats", SysStatsHandler)
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