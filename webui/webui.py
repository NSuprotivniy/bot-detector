import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options
import base64
import os

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

def encode(col):
	le = LabelEncoder()
	le.fit(col)
	return le.transform(col)
	
class HeadersModel():
	model = None
	X = None
	y = None
	def loadData(self, dataFile, sampleSize):
		http = pq.read_table("data\\" + dataFile).to_pandas().head(sampleSize)
		self.X = http[[
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
		self.y = http['isBot']
	def train(self):
		self.model = RandomForestClassifier(n_estimators=5, 
			max_depth = 19,  
			max_features = 15,
			n_jobs=-1, 
			random_state=17)
		self.model.fit(X, y)
	def predict(self, data):
		pass # TODO
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
		plt.savefig("graph\\" + 'result.png', dpi=60)
		plt.close()
		
	
def headers_test(dataFile, sampleSize):
	headers = HeadersModel()
	headers.loadData(dataFile, sampleSize)
	headers.test()

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", IndexHandler),
			(r"/upload", UploadHandler),
			(r"/deletedata/*", DeleteHandler),
			(r"/headersTest", HeadersMethodTest)
		]
		tornado.web.Application.__init__(self, handlers)

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		files = os.listdir("data")
		self.render("templates/index.html", files=files)
		
class UploadHandler(tornado.web.RequestHandler):
	def post(self):
		file1 = self.request.files['data'][0]
		original_fname = file1['filename']
		extension = os.path.splitext(original_fname)[1]
		if(extension != ".parquet"):
			self.set_status(300)
			self.finish()
			return
		if(os.path.isfile("data/" + original_fname)):
			self.set_status(201)
		output_file = open("data/" + original_fname, 'wb')
		output_file.write(file1['body'])
		self.finish(original_fname)
		
class DeleteHandler(tornado.web.RequestHandler):
	def delete(self):
		name = self.request.body
		try:
			name = name.decode("utf-8")
			os.remove("data/"+name)
			self.set_status(200)
			self.finish()
		except:
			self.set_status(404)
			self.finish()
			
class HeadersMethodTest(tornado.web.RequestHandler):
	def post(self):
		params = self.request.body.decode("utf-8")
		params = params.split(" ")
		print(params)
		headers_test(params[0], int(params[1]))
		with open("graph/result.png", "rb") as imageFile:
			imageBase64 = base64.b64encode(imageFile.read())
		self.finish(imageBase64)

def main():
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()