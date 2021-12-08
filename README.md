# CMPT 353 Project

| Name | SFU ID |
|---|---|
| Pin-Jiun Tseng | pta32 |
| Tony Ma | matonym |
|  | vineshr |

### Sensors, Noise, and Walking

[Sensors, Noise, and Walking](https://coursys.sfu.ca/2021fa-cmpt-353-d1/pages/ProjectWalking)

## Usage

### `walk-speed.py`

Required libraries: `matplotlib`, `pandas`, `scipy`, `sys`

#### Input

```
$ python3 walk-speed.py [LEFT LEG DATA] [RIGHT LEG DATA]
```

#### Output

- Individual output files with suffix '-walk-speed' for left and right containing 'time', 'ax', 'butterworth', 'delta_v', 'velocity', 'displacement'  
- *Output files are placed under data folder*  
  
#### Example

```
$ python3 walk-speed.py data/left_ankle_3min.csv data/right_ankle_3min.csv  
```

### `gait_difference.py`

Required libraries: `matplotlib`, `pandas`, `scipy`, `sys`

#### Input

```
$ python3 gait_difference.py [LEFT LEG DATA] [RIGHT LEG DATA]
```

### Output

Message printed on the terminal that indicates whether or not the data sets pass the T-test or not, and if the step count difference is within the significance level (default: 0.05).

#### Example

```
$ python gait_difference.py data/left_ankle_3min.csv data/right_ankle_3min.csv
```
