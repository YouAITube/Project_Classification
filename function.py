# -*- coding: utf-8 -*-
"""function.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TAleFSo2dj9d5hoYvh6a8It5h4345_qw
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import StandardScaler ,MinMaxScaler,LabelEncoder
#from category_encoders import TargetEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
import scipy.stats as stats
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score as acc
from sklearn.metrics import f1_score as f1
from sklearn.preprocessing import OneHotEncoder,OrdinalEncoder
from sklearn.model_selection import GridSearchCV
from sklearn.impute import KNNImputer
from sklearn.base import BaseEstimator
from sklearn.metrics import precision_score, recall_score, confusion_matrix, classification_report, roc_curve, precision_recall_curve
import itertools
from sklearn.model_selection import train_test_split
import scipy.stats as stats
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_validate
from sklearn.base import BaseEstimator

import warnings
warnings.filterwarnings("ignore")

def dataframe_info(df):
    print("dataframe shape is :", df.shape)
    columns_x = df.copy()
    tmp = []

    for col in columns_x:
        ser = df[col]
        tmp.append({
            'name': ser.name,
            'dtype': str(ser.dtype),
            'n_unique': len(ser.unique()),
            'n_null': ser.isnull().sum(),
        })
    df_info = pd.DataFrame(tmp)
    display(df_info)

def duplicates(data : pd.DataFrame) -> pd.DataFrame:
  print('old shape is' ,data.shape)
  if data.duplicated().any() == True:
    #check for duplicate rows based on all columns
    duplicates_all_columns = data[data.duplicated()]
    display(duplicates_all_columns.head(2))
    #To count the number of duplicates
    num_duplicates = data.duplicated().sum()
    print("duplicated values are : " ,num_duplicates)

    data.drop_duplicates( keep='first',inplace=True)
  print("new shape is : ")
  display(data.shape)

  return data


def nan_values_handle(data):
  print("missing_values")
  print("data_shape :" ,data.shape)
  percent_missing = data.isnull().sum() * 100 / len(data)
  missing_value_df = pd.DataFrame({'column_name': data.columns,
                                 'percent_missing': percent_missing})
  display(missing_value_df.sort_values(ascending=False,by="percent_missing")[:50])

  print("drop_cols_with_more_then_nan_values_0.6%")
  missing_data_high=missing_value_df["percent_missing"]>10
  display(missing_data_high[missing_data_high==True].index)

  drop_cols=missing_data_high[missing_data_high==True].index
  data.drop(drop_cols,axis=1,inplace=True)
  display(data.shape)
  return data

def split(X,y):
   X_train, X_val, y_train, y_val = train_test_split(X,y,
                                                    test_size=0.2,
                                                    random_state=42)
   print('Training Features Shape:', X_train.shape)
   print('Training Labels Shape:', y_train.shape)
   print('Testing Features Shape:', X_val.shape)
   print('Testing Labels Shape:', y_val.shape)
   return X_train,X_val,y_train,y_val


def result(X_train,X_val,y_train,y_val,estimator):
  best=estimator
  best.fit(X_train, y_train)

  y_predict=best.predict(X_val)

  scoring = {'ACC': 'accuracy',
             'F1': 'f1',
             'Precision': 'precision',
             'Recall': 'recall'}

  scores = cross_validate(best, X_train, y_train,
                         scoring=scoring, cv=StratifiedKFold(n_splits=5, shuffle = True, random_state=42),
                         return_train_score=True)


  print('croos_validate''s results  ')
  DF_cv = pd.DataFrame(scores)
  display(DF_cv)
  print('\n')
  print(DF_cv.mean()[2:])

  print(classification_report(y_val, y_predict, target_names=['canceled','not canceled']))

def curve(y_val,y_predict):
  from sklearn.metrics import auc

  # Calculate precision-recall curve
  precision, recall, _ = precision_recall_curve(y_val,
                                                y_predict)

  # Calculate area under the precision-recall curve
  auc_pr = auc(recall, precision)

  # Plot precision-recall curve
  plt.plot(recall, precision, label=f'AUC-PR = {auc_pr:.2f}')
  plt.xlabel('Recall')
  plt.ylabel('Precision')
  plt.title('Precision-Recall Curve')
  plt.legend()
  plt.show()

def plot_confusion_matrix(cm, classes,normalize=False):
    plt.figure(figsize = (5,5))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion matrix')
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('Actual')
    plt.xlabel('Predicted')

def show_metrics(cm):
    tp = cm[1,1]
    fn = cm[1,0]
    fp = cm[0,1]
    tn = cm[0,0]
    print('Precision =     {:.3f}'.format(tp/(tp+fp)))
    print('Recall    =     {:.3f}'.format(tp/(tp+fn)))
    print('F1_score  =     {:.3f}'.format(2*(((tp/(tp+fp))*(tp/(tp+fn)))/
                                                 ((tp/(tp+fp))+(tp/(tp+fn))))))


class LogisticRegressionWithThreshold(LogisticRegression):
    def predict(self, X, threshold=None):
        if threshold == None: # If no threshold passed in, simply call the base class predict, effectively threshold=0.5
            return LogisticRegression.predict(self, X)
        else:
            y_scores = LogisticRegression.predict_proba(self, X)[:, 1]
            y_pred_with_threshold = (y_scores >= threshold).astype(int)

            return y_pred_with_threshold


    def threshold_from_optimal_f_score(self, X, y):
        y_scores = LogisticRegression.predict_proba(self, X)[:, 1]
        precisions, recalls, thresholds = precision_recall_curve(y, y_scores)

        fscores = (2 * precisions * recalls) / (precisions + recalls)

        optimal_idx = np.argmax(fscores)

        return thresholds[optimal_idx], fscores[optimal_idx]