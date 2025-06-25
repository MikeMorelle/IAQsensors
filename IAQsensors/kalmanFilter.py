from pykalman import KalmanFilter
import pandas as pd

def kalman_filter(series):
    kf = KalmanFilter(
        transition_matrices = [[1, 1], [0, 1]], 
        observation_matrices = [[0.1, 0.5], [-0.3, 0.0]]
        )
    values = series.values.reshape(-1, 1)
    
    state_means, _ = kf.smooth(values)
    return pd.Series(state_means.flatten(), index=series.index)