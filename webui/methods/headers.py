import pickle
import base64
import copy
import json
import os

# ml dependencies
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import seaborn as sns
#import user_agents
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
		data["html"] = ""
		data["script"] ="""function renderResult() {
						var ul = document.createElement('ul');
						ul.className = 'list-group';
						container.appendChild(ul);
						arr = jsonData['array'];
						for (var entry in arr) {
							var li = document.createElement('li');
							li.className = 'list-group-item';
							li.innerHTML = arr[entry]["userId"] + " " + arr[entry]['proba'];
							ul.appendChild(li);
							}
						}
						"""
		data["data"] = {}
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
		data["html"] = "<img id='resultGraph' src=''/>";
		data["script"] ="""function renderResult() { 
						var rawImg1 = scriptData['rawImg1']; 
						$('#resultGraph').attr('src','data:image/gif;base64,'+rawImg1);}
						"""
		data["data"] = {}
		data["data"]["rawImg1"] = imageBase64.decode("ascii")
		return data
		
	def saveModel(self, name):
		filename = os.path.join(MODELS_DIR, self.modelType, name + "." + self.type_file_extension)
		save = [self.model, self.labels]
		pickle.dump(save, open(filename, 'wb'))
		data = {}
		data['name'] = name + "." + self.type_file_extension
		return data
		
	def loadModel(self, name):
		filename = os.path.join(MODELS_DIR, self.modelType, name)
		save = pickle.load(open(filename, 'rb'))
		self.model = save[0]
		self.labels = save[1]