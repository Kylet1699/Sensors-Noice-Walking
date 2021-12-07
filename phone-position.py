#!/usr/bin/env python
# coding: utf-8

# In[31]:


import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal, stats
import numpy as np
import glob
import sys

#EX: python3 phone-position.py ankle_3min pocket_3min
OUTPUT = (
    'P value x unfiltered: {pxuf} P value filtered: {pxf}\n'
    'P value y unfiltered: {pyuf} P value filtered: {pyf}\n'
    'P value z unfiltered: {pzuf} P value filtered: {pzf}'
)


# In[32]:


#Function used to combine both left and right side data of a person into 1 dataframe
#Taken and modified from https://stackoverflow.com/questions/20906474/import-multiple-csv-files-into-pandas-and-concatenate-into-one-dataframe
def get_files(dataset):
    all_data = glob.glob('data/' + '*' + dataset + '*.csv')
    temp_list = []
    for i in all_data:
        temp_df = pd.read_csv(i)
        if('wx' in temp_df.columns):
            #Call trim here
            temp_df = trim(temp_df)
            temp_list.append(temp_df)
    if not temp_list:
        return
    data = pd.concat(temp_list)
    return data

#Trim data
def trim(data):
    #remove the first and last 1-3000 datapoints, and uneeded columns
    data = data[3000:-2000]
    data = data.reset_index(drop = True)
    return data[['wx','wy','wz']]

def butterworth(data):
    # Numerator(b) and denominator (a) polynomials of the IIR filter
    # fc = cut-off frequency of the filter
    # fs = sampling frequency of phone
    # w = fc/(fs/2)
    fc = 5
    fs = 418
    w = fc/(fs/2)
    b, a = signal.butter(5, w, btype = 'highpass', analog=False)
    # Filter data 
    low_passed_x = signal.filtfilt(b, a, data['wx'])
    low_passed_y = signal.filtfilt(b, a, data['wy'])
    low_passed_z = signal.filtfilt(b, a, data['wz'])
    data['wx_fil'] = low_passed_x
    data['wy_fil'] = low_passed_y
    data['wz_fil'] = low_passed_z
    return data

def plot(data, data2, title):
    fig, axs = plt.subplots(3,2, figsize = (20,15), constrained_layout=True)
    fig.suptitle(title)
    axs[0,0].plot(data['wx_fil'])
    axs[0,0].set_title('Ankle X')
    axs[0,0].set_xlim([0,2000])
    axs[0,0].set_ylim([-10, 10])
    
    axs[0,1].plot(data2['wx_fil'])
    axs[0,1].set_title('Pocket X')
    axs[0,1].set_xlim([0,2000])
    axs[0,1].set_ylim([-10, 10])
    
    axs[1,0].plot(data['wy_fil'])
    axs[1,0].set_title('Ankle Y')
    axs[1,0].set_xlim([0,2000])
    axs[1,0].set_ylim([-10, 10])
    
    axs[1,1].plot(data2['wy_fil'])
    axs[1,1].set_title('Pocket Y')
    axs[1,1].set_xlim([0,2000])
    axs[1,1].set_ylim([-10, 10])
    
    axs[2,0].plot(data['wz_fil'])
    axs[2,0].set_title('Ankle Z')
    axs[2,0].set_xlim([0,2000])
    axs[2,0].set_ylim([-10, 10])
    
    axs[2,1].plot(data2['wz_fil'])
    axs[2,1].set_title('Pocket Z')
    axs[2,1].set_xlim([0,2000])
    axs[2,1].set_ylim([-10, 10])
    
    plt.savefig('Ankle vs Pocket')
    
def main():
    #function that takes all the ankle and pocket csvs (with gyroscope data recorded) and sorts them into
    #2 seperate dataframes
    
    ankle = get_files(sys.argv[1])
    pocket = get_files(sys.argv[2])
    
#     ankle = pd.read_csv('data/left_ankle_400m.csv')
#     pocket = pd.read_csv('data/left_pocket_400m.csv')

    #butterworth filter to clean it
    
    ankle = butterworth(ankle)
    pocket = butterworth(pocket)
    
    #Manwhitney test data before cleaning it and plotting
    pval_x_before = stats.mannwhitneyu(ankle['wx'], pocket['wx'], alternative = 'two-sided').pvalue
    pval_y_before = stats.mannwhitneyu(ankle['wy'], pocket['wy'], alternative = 'two-sided').pvalue
    pval_z_before = stats.mannwhitneyu(ankle['wz'], pocket['wz'], alternative = 'two-sided').pvalue
    
    #redo ttest after filter
    pval_x_filter = stats.mannwhitneyu(ankle['wx_fil'], pocket['wx_fil'], alternative = 'two-sided').pvalue
    pval_y_filter = stats.mannwhitneyu(ankle['wy_fil'], pocket['wy_fil'], alternative = 'two-sided').pvalue
    pval_z_filter = stats.mannwhitneyu(ankle['wz_fil'], pocket['wz_fil'], alternative = 'two-sided').pvalue
    #output p values and plot difference
    print(OUTPUT.format(
        pxuf = pval_x_before,
        pxf = pval_x_filter,
        pyuf = pval_y_before,
        pyf = pval_y_filter,
        pzuf = pval_z_before,
        pzf = pval_z_filter))
    plot(ankle, pocket, 'Ankle vs Pocket Filtered Data Comparison')
    
    
    
if __name__ == '__main__':
    main()

