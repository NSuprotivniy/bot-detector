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
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib

from time import time

# ml dependencies

TEMPLATES_DIR = "templates"
DATA_DIR = "data"
MODELS_DIR = "models"
GRAPH_DIR = "graph"

class HeadersModel():
	clf = None
	ohe = None
	ht = None
	modelType = "headers"
	type_file_extension = "hdr"
	start_time = 0

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

	def predict(self, request_data):
		df_row = pd.DataFrame(columns=self.FEATURES)
		row = []
		for feature in self.FEATURES:
			try:
				row.append(request_data[feature])
			except KeyError:
				row.append("")
		df_row.loc[0] = row
		print(row)
		df_row = self.ht.transform(df_row)
		df_row = self.ohe.transform(df_row)
		print(self.clf.predict_proba(df_row))
		return { 'timestamp' : time() - self.start_time, 'proba' : self.clf.predict_proba(df_row)[0][1] }

	def loadModel(self, name):
		save = joblib.load(name + '.clf')
		self.clf = save
		save = joblib.load(name + '.ht')
		self.ht = save
		save = joblib.load(name + '.ohe')
		self.ohe = save
