import numpy as np
import pandas as pd
import sys
from scipy import signal
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

# Can you calculate walking speed (m/s) from just the accelerometer? 
# How accurate can you get? 
# Can you then determine differences between subjects as above?

# Get data from sys.argv[1]
def get_data(filename):
    data = pd.read_csv(filename)
    # data.rename(columns = {'time': 'time(ms)'}, inplace = True)
    return data

# Clean up the data
def filter_data(left, right):
    left = left[['time', 'ax']]
    right = right[['time', 'ax']]
    reverse_orientation = lambda x : x * (-1) if x != 0 else x
    right['ax'] = right['ax'].apply(reverse_orientation)
    left = left.rename(columns={'time': 'time_left', 'ax' : 'ax_left'})
    right = right.rename(columns={'time': 'time_right', 'ax' : 'ax_right'})
    data = left.join(right).fillna(0)
    return data

def plot(data):
    plt.figure(figsize=(16,6))
    plt.title('Left') 
    plt.plot(data['time_left'], data['ax_left'], 'b.', alpha = 0.5, label = 'Left velocity')
    plt.plot(data['time_left'], data['butterworth_right'], 'r')
    plt.show()
    plt.figure(figsize=(16,6))
    plt.title('Right')
    plt.plot(data['time_left'], data['ax_right'], 'b.', alpha = 0.5)
    plt.plot(data['time_left'], data['butterworth_right'], 'r')
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
    low_passed = signal.filtfilt(b, a, data['ax_left'])
    data['butterworth_left'] = low_passed
    low_passed = signal.filtfilt(b, a, data['ax_right'])
    data['butterworth_right'] = low_passed
    return data

# def fourier(data):
#     n = len(data.index) # number of points
#     Lx = data['time'][-1:0] # time period (ms)
    
# Calculate velocity from acceleration
# Δv = a⋅Δt and Δp = v⋅Δt.
# get the initial velocity
# velocity is delta_v + velocity from preious point
def vel(data):
    data_shifted = data.shift(1)
    delta_t_left = data['time_left'] - data_shifted['time_left']
    delta_t_right = data['time_right'] - data_shifted['time_right']
    print(delta_t_left.mean())
    print(delta_t_right.mean())
    print("average left", data['butterworth_left'].mean())
    print("average_right", data['butterworth_right'].mean())
    delta_v_left = delta_t_left * data['butterworth_left']
    delta_v_right = delta_t_right * data['butterworth_right']
    print(delta_v_left.mean())
    print(delta_v_right.mean())
    delta_v_left = pd.DataFrame(delta_v_left, columns=['delta_v_left'])
    delta_v_right = pd.DataFrame(delta_v_right, columns=['delta_v_right'])
    data = data.join(delta_v_left)
    data = data.join(delta_v_right)
    data['velocity_left'] = 0
    data['velocity_right'] = 0
    data.at[0, 'delta_v_left'] = 0
    data.at[0, 'delta_v_right'] = 0
    for index, row in data.iterrows():
        data.loc[index, 'velocity_left'] = data.iloc[index]['delta_v_left'] + data.iloc[index-1]['velocity_left']
        data.loc[index, 'velocity_right'] = data.iloc[index]['delta_v_right'] + data.iloc[index-1]['velocity_right']
    data['displacement_left'] = data['velocity_left'] * delta_t_left
    data['displacement_right'] = data['velocity_right'] * delta_t_right
    return data

def main(input1, input2, output_file):
    left = get_data(input1)
    right = get_data(input2)
    # Clean up the data for later
    data = filter_data(left, right)
    # Performs Butterworth filter on the data
    data = butterworth(data)
    # Adds velocity to data
    data['butterworth_right'] = data['butterworth_right'] + 0.1
    data = vel(data)

    print(data)
    print("Left distance walked: ", data['displacement_left'].sum())
    print("Right distance walked: ", data['displacement_right'].sum())


    plot(data)
    data.to_csv(output_file + 'walk-speed')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])