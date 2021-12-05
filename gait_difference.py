import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal, stats


def plot_data(left, right):
    # plot raw data
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle('Left and right ankle gyroscope data')
    ax1.plot(left['wx'], label='Gyroscope X')
    ax1.plot(left['wy'], label='Gyroscope Y')
    ax1.plot(left['wz'], label='Gyroscope Z')
    ax1.legend()
    ax1.set_xlim([4000, 6000])
    ax1.set_ylim([-10, 10])
    ax2.plot(right['wx'], label='Gyroscope X')
    ax2.plot(right['wy'], label='Gyroscope Y')
    ax2.plot(right['wz'], label='Gyroscope Z')
    ax2.legend()
    ax2.set_xlim([2000, 4000])
    ax2.set_ylim([-10, 10])
    plt.show()


def butterworth(data):
    # Numerator(b) and denominator (a) polynomials of the IIR filter
    # fc = cut-off frequency of the filter
    # fs = sampling frequency (418hz for Galaxy s9)
    # w = fc/(fs/2)
    fc = 5
    fs = 418
    w = 5/(418/2)
    b, a = signal.butter(4, w, btype = 'highpass', analog=False)
    # Filter data 
    low_passed_x = signal.filtfilt(b, a, data['wx'])
    low_passed_y = signal.filtfilt(b, a, data['wy'])
    low_passed_z = signal.filtfilt(b, a, data['wz'])
    data['wx'] = low_passed_x
    data['wy'] = low_passed_y
    data['wz'] = low_passed_z
    return data


# Get data from sys.argv[1]
def get_data(filename):
    data = pd.read_csv(filename)
    # data.rename(columns = {'time': 'time(ms)'}, inplace = True)
    return data


def main(left_input_file, right_input_file):
    left_data = get_data(left_input_file)
    right_data = get_data(right_input_file)

    # filter all unnecessary data remove data close
    # to beginning and close to end of data
    left_filtered = left_data[['wx', 'wy', 'wz']][2000:][:-2000]
    right_filtered = right_data[['wx', 'wy', 'wz']][2000:][:-2000]

    # trim data to make left and right data the same length
    if (left_filtered.shape[0] > right_filtered.shape[0]):
        difference = left_filtered.shape[0] - right_filtered.shape[0]
        left_filtered = left_filtered[:-difference]
    else:
        difference = right_filtered.shape[0] - left_filtered.shape[0]
        right_filtered = right_filtered[:-difference]

    # plot raw data
    # plot_data(left_filtered, right_filtered)

    # run data through butterworth 
    left_filtered = butterworth(left_filtered)
    right_filtered = butterworth(right_filtered)

    # plot filtered data
    # plot_data(left_filtered, right_filtered)

    # combine x y z into one data point
    left_filtered['average'] = (left_filtered['wx'] + left_filtered['wy'] + left_filtered['wz']) / 3
    right_filtered['average'] = (right_filtered['wx'] + right_filtered['wy'] + right_filtered['wz']) / 3

    # test if data passes normal test and equal variance test
    if stats.normaltest(left_filtered['average']).pvalue < 0.05 and stats.normaltest(right_filtered['average']).pvalue < 0.05:
        print('[NOTE] Data is normally distributed')
        if (stats.levene(left_filtered['average'], right_filtered['average']).pvalue < 0.05):
            print('[NOTE] Data is homoscedastic')
        else:
            print('[NOTE] Data ios not homoscedastic')
            quit()
    else:
        print('[ERROR] Data is not normally distributed')
        quit()

    # perform t test to determine if data is different
    ttest = stats.ttest_ind(left_filtered['average'], right_filtered['average'])
    if ttest.pvalue < 0.05:
        print('The data from the left and right ankle pass the t-test, and we must conclude that the gait is the same')
    else:
        print('The data from the left and right ankle do not pass the t-test, and we can conclude that the gait is different')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
