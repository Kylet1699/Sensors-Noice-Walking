import numpy as np
import pandas as pd
import sys
from scipy import signal
import matplotlib.pyplot as plt

# Can you calculate walking speed (m/s) from just the accelerometer? 
# How accurate can you get? 
# Can you then determine differences between subjects as above?
'''
INPUT:
    arg1: Left leg data csv file with accelerometer data containing column 'time', 'ax'
    arg2: Right leg data csv file with accelerometer data containig column 'time', 'ax'

OUTPUT:
    Individual output files with data containing 'time', 'ax', 'butterworth', 'delta_v', 'velocity', 'displacement'
'''

def get_data(filename):
    data = pd.read_csv(filename)
    data = data[['time', 'ax']]
    # Reverse +/- because phone is facing the opposite direction when attached to right leg
    if 'right' in filename:
        reverse_orientation = lambda x : x * (-1) if x != 0 else x
        data['ax'] = data['ax'].apply(reverse_orientation)    
    return data

def plot(data, title):
    plt.figure(figsize=(16,6))
    plt.title(title) 
    plt.plot(data['time'], data['ax'], 'b.', alpha = 0.5, label = 'Input')
    plt.plot(data['time'], data['butterworth'], 'r', label = 'Butterworth')
    plt.legend()
    plt.show()

def butterworth(data):
    # Numerator(b) and denominator (a) polynomials of the IIR filter
    # fc = cut-off frequency of the filter
    # fs = sampling frequency (418hz for Galaxy s9)
    # w = fc/(fs/2)
    fc = 4
    fs = 418
    w = fc/(fs/2)
    b, a = signal.butter(fc, w, btype = 'highpass', analog=False)
    # Filter data 
    low_passed = signal.filtfilt(b, a, data['ax'])
    data['butterworth'] = low_passed
    return data

# Calculate velocity from acceleration
# Δv = a⋅Δt and Δp = v⋅Δt.
# get the initial velocity
# velocity is delta_v + velocity from preious point
def vel(data):
    data_shifted = data.shift(1)
    delta_t = data['time'] - data_shifted['time']
    delta_v = delta_t * data['butterworth']

    # Put delta_v in dataframe to join with main dataframe
    delta_v = pd.DataFrame(delta_v, columns=['delta_v'])
    data = data.join(delta_v)

    data['velocity'] = 0
    data.at[0, 'delta_v'] = 0

    for index, row in data.iterrows():
        data.loc[index, 'velocity'] = data.iloc[index]['delta_v'] + data.iloc[index-1]['velocity']

    # Calculate displacement
    data['displacement'] = data['velocity'] * delta_t
    return data

def main(input1, input2):
    # Gets data from input files and filter them
    left = get_data(input1)
    right = get_data(input2)

    # Performs Butterworth filter on the data
    left_filtered = butterworth(left)
    right_filtered = butterworth(right)

    # Calculate velocity, displacement
    # data['butterworth_right'] = data['butterworth_right'] + 0.1
    left_filtered = vel(left_filtered)
    right_filtered = vel(right_filtered)

    print(left_filtered)
    print(right_filtered)
    print("Left distance walked: ", left_filtered['displacement'].sum())
    print("Right distance walked: ", right_filtered['displacement'].sum())
    print("Average left walking speed (m/s): ", left_filtered['velocity'].mean())
    print("Average right walking speed (m/s): ", right_filtered['velocity'].mean())

    plot(left_filtered, 'Left')
    plot(right_filtered, 'Right')
    left_filtered.to_csv(input1 + '-output')
    right_filtered.to_csv(input1 + '-output')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])