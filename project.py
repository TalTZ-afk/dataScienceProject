import time
import os

import pandas as pd
import scipy as sc
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from sklearn import linear_model, metrics, preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


df = pd.DataFrame()
# coulmn is a column of scores from the website "Metascore" (taken from each of the films sites),
# added after evaluating the prediction (went from 0.43 to 0.67)
column = pd.DataFrame()

# because my data set was vreated from 10 different files it created 10 different files,
# this function unites them if needed
def unite_df():
    df_new = pd.DataFrame()
    for i in range(0,10):
        df_raw = pd.read_csv('df_raw/df' + str(i) + '.csv')
        df_new = pd.concat([df_new, df_raw], ignore_index=True)
    return df_new

# the same as "unite_df" but for column
def unite_column():
    column_new = pd.DataFrame()
    for i in range(0,10):
        column_raw = pd.read_csv('column_raw/column' + str(i) + '.csv')
        column_new = pd.concat([column_new, column_raw], ignore_index=True)
    return column_new

def outlier_detection_iqr(df):
    cols = ["number_of_users_rating", "budget", "gross"]
    for col in cols:
        Q1 = np.percentile(df[col], 25)
        Q3 = np.percentile(df[col], 75)
        IQR = Q3 - Q1
        IQR_range = 6 * IQR
        df[col][(df[col] < Q1 - IQR_range) | (df[col] > Q3 + IQR_range)] = np.nan
    return df.copy()

def outlier_detection_zscore_dist(df):
    
    cols = ["number_of_users_rating", "budget", "gross"]
    
    for col in cols:
        z_score = (df[col] - df[col].mean()) / df[col].std()
        outliers = abs(z_score) > 3
        df[col][outliers] = np.nan
    return df.copy()

# df = unite_df()
# df.to_csv('df.csv')
df = pd.read_csv('df.csv')
# column = unite_column()
# column.to_csv('column.csv')
column = pd.read_csv('column.csv')
df = df.assign(metascore = column.values)

# cleaning the data
df = df.drop_duplicates()
df = df.dropna()
# changing veraity of values that represent the same thing into one
df["motion_picture_rating"] = df["motion_picture_rating"].replace("Approved", "UR")
df["motion_picture_rating"] = df["motion_picture_rating"].replace("Not Rated", "UR")
df["motion_picture_rating"] = df["motion_picture_rating"].replace("Unrated", "UR")
df["motion_picture_rating"] = df["motion_picture_rating"].replace("Passed", "UR")
df["motion_picture_rating"] = df["motion_picture_rating"].replace("X", "NC-17")

# changing values for director and stars rating so they can beacome a categorical data,
# and declaring them as such
for value in df.director_rated:
    if len(value) <= 3 and value != "Low":
        df["director_rated"] = df["director_rated"].replace(value, "Top 100")

df['director_rated'] = df['director_rated'].astype('category')

for value in df.star_1_rated:
    if len(value) <= 3 and value != "Low":
        df["star_1_rated"] = df["star_1_rated"].replace(value, "Top 100")

df['star_1_rated'] = df['star_1_rated'].astype('category')

for value in df.star_2_rated:
    if len(value) <= 3 and value != "Low":
        df["star_2_rated"] = df["star_2_rated"].replace(value, "Top 100")

df['star_2_rated'] = df['star_2_rated'].astype('category')

for value in df.star_3_rated:
    if len(value) <= 3 and value != "Low":
        df["star_3_rated"] = df["star_3_rated"].replace(value, "Top 100")

df['star_3_rated'] = df['star_3_rated'].astype('category')

replace_dic = {'Low':0, 'Top 5000':1, 'Top 500':2, 'Top 100':3}
df.replace(replace_dic, inplace=True)

bins = [0,50001,100001,300001,2500001]
labels = [0,1,2,3]
df['number_of_users_rating_binned'] = pd.cut(df['number_of_users_rating'], bins, labels=labels)

df['metascore'][(df['metascore'] == 0)] = np.nan
df = df.dropna()

# box plots of "number_of_users_rating", "budget" and "gross"
sns.boxplot(df.number_of_users_rating, whis=1.5)
plt.show()

sns.boxplot(df.budget, whis=1.5)
plt.show()

sns.boxplot(df.gross, whis=1.5)
plt.show()

# cross tabulation of "director_rated", "star_1_rated", "star_2_rated", "star_3_rated" and "imdb_rating_binned"
# using bar plot to show their relative frequencies according to "imdb_rating_binned"
# "#" added so "imdb_rating_binned" won't intterupt with the prediction
# bins = [0,2.9,4.9,6.9,8.9,10]
# labels = ['1-2','3-4','5-6','7-8','9+']
# df['imdb_rating_binned'] = pd.cut(df['imdb_rating'], bins, labels=labels)

# fig, axes = plt.subplots(1,4)

# ct0 = pd.crosstab(df['imdb_rating_binned'], df['director_rated'], normalize='index')
# ct0.plot(kind='bar', ax=axes[0])

# ct1 = pd.crosstab(df['imdb_rating_binned'], df['star_1_rated'], normalize='index')
# ct1.plot(kind='bar', ax=axes[1])

# ct2 = pd.crosstab(df['imdb_rating_binned'], df['star_2_rated'], normalize='index')
# ct2.plot(kind='bar', ax=axes[2])

# ct3 = pd.crosstab(df['imdb_rating_binned'], df['star_3_rated'], normalize='index')
# ct3.plot(kind='bar', ax=axes[3])

# plt.show()

# 3D scatter plot wit "gross" as x, "budget" as y and "imdb_rating" as z
ax = plt.axes(projection='3d')
xdata = df.gross
ydata = df.budget
zdata = df.imdb_rating
ax.scatter3D(xdata, ydata, zdata, c=zdata, depthshade=False)
plt.show()

# scatter plot showing connections between "budget", "gros" and "imdb_rating_binned"
# "#" added so "imdb_rating_binned" won't intterupt with the prediction
# sns.scatterplot(x='budget', y='gross', hue='imdb_rating_binned', data=df)
# plt.show()
# scatter plot showing connections between "budget", "gros", "imdb_rating_binned" and "metascore"
# (added after evaluation of the prediction)
# "#" added so "imdb_rating_binned" won't intterupt with the prediction
# sns.scatterplot(x='budget', y='gross', hue='imdb_rating_binned', size='metascore', sizes=(1,100), data=df)
# plt.show()

# deviding into feature vector and label vector
X = df.copy()
y = X['imdb_rating']
X.drop(['imdb_rating', 'movie_title', 'director_name', 'star_1_name', 'star_2_name', 'star_3_name', 'genres', 'motion_picture_rating', 'contry_of_origin', 'language', 'color'], axis=1, inplace=True)
# deviding into trains and tests
X_1st_train, y_1st_train, X_1st_test, y_1st_test = X.copy(), y.copy(), X.copy(), y.copy()
# creating the model
trained_model_1st = linear_model.LinearRegression().fit(X_1st_train, y_1st_train)
# creating the prediction
pred_1st_vals = trained_model_1st.predict(X_1st_test)
# implementing the prediction
y_pred_1st = pd.Series(pred_1st_vals, index=X_1st_test.index)
# evaluating the prediction
eval_res_1st = r2_score(y_1st_test, y_pred_1st)
print(eval_res_1st)