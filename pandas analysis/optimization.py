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
import blackbox as bb

DATA_DIR = 'S:\\data\\'
GRAPH_PATH = 'S:\\graph\\'
SAMPLE_SIZE = 10000 # -1 если использовать все даннные
DEPTH_RANGE = range(1, 20, 2)
KNN_NEIGHBORS_RANGE = range(1, 20, 2)

forest = None
X = None
y = None

def encode(col):
	le = LabelEncoder()
	le.fit(col)
	return le.transform(col)

def bb_func(params):
	print("bb_func called...")
	global forest, X, y
	forest.max_depth = params[0]
	forest.max_features = params[1]
	return -1*f1_score(y, classifier.predict(X))	
   

SAMPLE_SIZE_RANGE = range(1000, 2000, 1000)
sample_range = SAMPLE_SIZE_RANGE
best_scores_grid_search = []

for sample_size in sample_range:
	http = pq.read_table(DATA_DIR + 'botsHTTPRequests-20180217_1718_parsedUA.parquet').to_pandas().head(sample_size)

	X = http[[
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
	y = http['isBot']
	rows, feats = X.shape
	X_train, y_train = X, y
	forest = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=17)

	# grid search
	"""
	forest_params = {'max_depth': DEPTH_RANGE,'max_features': range(1,feats)}
	forest_grid = GridSearchCV(forest, forest_params, cv=5, n_jobs=-1, verbose=True, scoring='f1')
	forest_grid.fit(X_train, y_train)
	# forest_grid.best_params_
	best_scores_grid_search.append(forest_grid.best_score_ )
	"""

	# blackbox optimization
	print("START")

	bb.search(f=bb_func,  # given function
		box=[DEPTH_RANGE, range(1,feats)],  # range of values for each parameter (2D case)
		n=4,  # number of function calls on initial stage (global search)
		m=2,  # number of function calls on subsequent stage (local search)
		batch=1,  # number of calls that will be evaluated in parallel
		resfile=GRAPH_PATH+'output.csv')  # text file where results will be saved

	print("...")
	print(best_scores_grid_search)
	print(sample_range)
    
plt.plot(sample_range, best_scores_grid_search, label='Grid search')
plt.title('Optimization scores')
plt.savefig(GRAPH_PATH + 'forest_optimization_scores.png', dpi=900)
plt.legend();

