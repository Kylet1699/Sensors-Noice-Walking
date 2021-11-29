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
def filter_data(data):
    data = data[['time', 'ax']]
    # data['ax'] = data['ax'].abs()
    return data

def plot(data): 
    plt.figure(1, figsize=(12, 4))
    plt.plot(data['time'], data['ax'], 'b.', alpha = 0.5)
    plt.plot(data['time'], data['butterworth'], 'r')
    plt.show()

def butterworth(data):
    # Numerator(b) and denominator (a) polynomials of the IIR filter
    b, a = signal.butter(3, 0.1, btype = 'lowpass', analog=False)
    # Filter data 
    low_passed = signal.filtfilt(b, a, data['ax'])
    data['butterworth'] = low_passed
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
    delta_t = data['time'] - data_shifted['time']
    delta_v = delta_t * data['ax']
    delta_v = pd.DataFrame(delta_v, columns=['delta_v'])
    data = data.join(delta_v)
    data['velocity'] = 0
    data.at[0, 'delta_v'] = 0
    for index, row in data.iterrows():
        data.loc[index, 'velocity'] = data.iloc[index]['delta_v'] + data.iloc[index-1]['velocity']
    data['displacement'] = data['velocity'] * delta_t
    return data

def main(input_file, output_file):
    data = get_data(input_file)
    # Clean up the data for later
    data = filter_data(data)
    # Performs Butterworth filter on the data
    data = butterworth(data)
    # Adds velocity to data
    data = vel(data)

    print(data)
    print(data['displacement'].sum())

    plot(data)
    data.to_csv(output_file)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])