import argparse
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal, stats

'''
INPUT:
    arg1: Left leg data csv file with gyroscope data containing columns 'wx', 'wy', 'wz'
    arg2: Right leg data csv file with gyroscope data containing columns 'wx', 'wy', 'wz'

OPTIONS:
    -s, --significance: Specify a significance level
    --plot-raw: Plot a graph of the raw data for both data files
    --plot-filtered: Plot a graph of the filtered data for both data files
'''


def plot_data(left, right, title, range=[0, 2000]):
    # Create subplot with two plots
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle(title)
    # Left subplot
    ax1.plot(left['wx'], label='X')
    ax1.plot(left['wy'], label='Y')
    ax1.plot(left['wz'], label='Z')
    ax1.legend()
    ax1.set_xlim(range)
    ax1.set_ylim([-10, 10])
    # Right subplot
    ax2.plot(right['wx'], label='X')
    ax2.plot(right['wy'], label='Y')
    ax2.plot(right['wz'], label='Z')
    ax2.legend()
    ax2.set_xlim(range)
    ax2.set_ylim([-10, 10])
    plt.show()


def butterworth(data):
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


def steps_analysis(left, right, significance):
    # Find the peaks above the middle of the data
    left_peaks, _ = signal.find_peaks(left, height=left.median())
    right_peaks, _ = signal.find_peaks(right, height=right.median())

    # Get the number of peaks
    left_steps = len(left_peaks)
    right_steps = len(right_peaks)

    # Check if the difference exceeds the significance level
    if ((left_steps if left_steps > right_steps else right_steps) /
        (right_steps if left_steps > right_steps else left_steps) -
        1 >
        significance):
        print(f'The step count difference exceed the significance level of {significance * 100}%.')
    else:
        print('There is no meaningful difference between the step count of the two data sets.')


def ttest_analysis(left, right, significance):
    # Test if data passes normal test and equal variance test before using the T-test on the two data sets
    if stats.normaltest(left).pvalue > significance or stats.normaltest(right).pvalue > significance:
        print('Error: Data is not normally distributed')
        quit()
    elif (stats.levene(left, right).pvalue > significance):
        print('Error: Data is not homoscedastic')
        quit()  

    # Perform T-test to determine if the data sets are different
    ttest = stats.ttest_ind(left, right)
    if ttest.pvalue < significance:
        print('The two data sets pass the t-test.')
    else:
        print('The two data sets do not pass the t-test.')


def main(left_input_file, right_input_file, plot_raw, plot_filtered, significance):
    '''
    left_input_file (string):  file path to the input file of left leg
    right_input_file (string): file path to ihe input file of right leg
    plot_raw (bool):           specify if plot raw data
    plot_filtered (bool):      specify if plot filtered data
    significance (float):      the significance level
    '''
    
    left_data = pd.read_csv(left_input_file)
    right_data = pd.read_csv(right_input_file)

    # Filter all unnecessary data and remove data close
    # to the beginning and close to the end of the data
    left_filtered = left_data[['wx', 'wy', 'wz']][2000:][:-2000]
    right_filtered = right_data[['wx', 'wy', 'wz']][2000:][:-2000]

    # Trim data to make left and right data the same length
    if (left_filtered.shape[0] > right_filtered.shape[0]):
        difference = left_filtered.shape[0] - right_filtered.shape[0]
        left_filtered = left_filtered[:-difference]
    else:
        difference = right_filtered.shape[0] - left_filtered.shape[0]
        right_filtered = right_filtered[:-difference]

    # Reset indices
    left_filtered = left_filtered.reset_index(drop=True)
    right_filtered = right_filtered.reset_index(drop=True)

    # Plot raw data if the option is specified
    if plot_raw:
        plot_data(left_filtered, right_filtered, 'Raw data')

    # Run data through Butterworth filter
    left_filtered = butterworth(left_filtered)
    right_filtered = butterworth(right_filtered)

    # Plot filtered data if the option is specified
    if plot_filtered:
        plot_data(left_filtered, right_filtered, 'Filtered data')

    # Combine x y z into one data point by taking the average
    left_filtered['average'] = (left_filtered['wx'] + left_filtered['wy'] + left_filtered['wz']) / 3
    right_filtered['average'] = (right_filtered['wx'] + right_filtered['wy'] + right_filtered['wz']) / 3

    # Perform the tests
    ttest_analysis(left_filtered['average'], right_filtered['average'], significance)
    steps_analysis(left_filtered['average'], right_filtered['average'], significance)


if __name__ == '__main__':
    # Add option to plot data 
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--significance', type=float, default=0.05, help='Significance level between 0 and 1')
    parser.add_argument('--plot-raw', action='store_true', help='Plot raw data')
    parser.add_argument('--plot-filtered', action='store_true', help='Plot filtered data')
    parser.add_argument('left_data_file', help='Left leg csv file with gyroscope data containing columns \'wx\', \'wy\', \'wz\'')
    parser.add_argument('right_data_file', help='Right leg csv file with gyroscope data containing columns \'wx\', \'wy\', \'wz\'')
    args = parser.parse_args()

    main(args.left_data_file, args.right_data_file, args.plot_raw, args.plot_filtered, args.significance)
