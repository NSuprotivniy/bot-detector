import pandas as pd
import pyarrow.parquet as pq
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn import metrics
from scipy.sparse import csr_matrix

DATA_DIR = '../../data/'
http_bots = pq.read_table(DATA_DIR + 'botsHTTPRequests-20180216_1416GMT.parquet').to_pandas()
http_users = pq.read_table(DATA_DIR + 'usersHTTPRequests-20180216_1416GMT.parquet').to_pandas()
http_users['target'] = 0
http_bots['target'] = 1
http = pd.concat([http_bots, http_users])
http = http.sample(frac=1).reset_index(drop=True)

print('Кол-во уникальных операций: {}'.format(len(http['operation'].unique())))


# Приведем категориальный столбей общей выборки к разряженному виду
# и разделим выборку на train и test

operations = http['operation']

dict_code_op = {}

c = 0
for op in operations.unique():
    dict_code_op[op] = c
    c += 1
    
operations = operations.apply(lambda x: dict_code_op[x])    

operations_sparse = csr_matrix(([1] * operations.shape[0],
                                operations,
                                range(0, operations.shape[0] + 1, 1)))[:, 1:]

# operations_sparse -> X_train/X_test; http.target -> y_train/y_test
idx_split = int(http.shape[0] * 0.7)
X_train = operations_sparse[:idx_split]
X_holdout = operations_sparse[idx_split:] #X_test = operations_sparse[idx_split:, :] для df
y_train = http['target'][:idx_split]
y_holdout = http['target'][idx_split:]                                


# Обучим модель
logit = LogisticRegression(C=0.1, n_jobs=-1, random_state=17)
logit.fit(X_train, y_train)                                

holdout_pred = logit.predict_proba(X_holdout)     

print('roc_auc: {}'.format(roc_auc_score(y_holdout, holdout_pred[:, 1])))

# P >= 0.5 => 1
res = []
arr = holdout_pred[:, 1]
type(arr)
for i in arr:
    if i >= 0.5: res.append(1)
    else: res.append(0)
    
print(metrics.classification_report(y_holdout, res))




