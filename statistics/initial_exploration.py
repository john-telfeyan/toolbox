#python=3.6
# -*- coding: utf-8 -*-
"""
Synopsis: initial data visualizations 

Created: Created on Tue Nov 26 23:12:58 2019

Sources:

Author:   John Telfeyan
          john <dot> telfeyan <at> gmail <dot> com

Distribution: MIT Opens Source Copyright; Full permisions here:
    https://gist.github.com/john-telfeyan/2565b2904355410c1e75f27524aeea5f#file-license-md
         
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('fivethirtyeight')

INPUT_FILE = "sample_data//rtb100k.csv"

if __name__=="__main__":
    df = pd.read_csv(INPUT_FILE, delimiter=';')
    print(df.dtypes)
    df.head()

    
