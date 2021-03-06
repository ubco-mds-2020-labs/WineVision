import pandas as pd
import numpy as np

wine = pd.read_csv("data/wine_new.csv")
wine.columns = wine.columns.map(' in '.join)
wine = wine.rename(columns = {'pH in Unnamed: 8_level_1':'pH', 'quality in Unnamed: 11_level_1':'quality'})
wine['Taste'] = np.where(wine['quality']<6, 'Below average', (np.where(wine['quality']>6.5, 'Above average', 'Average')))

wine.head()