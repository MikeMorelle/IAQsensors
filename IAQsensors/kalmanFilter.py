import pandas as pd
import numpy as np

#only using measured data (no external prediction)
def kalman_filter_self_predicting(measured, Q=1e-5, R=0.1, P_init=1.0, x_init=None):
    """
    kf = optimized autoregressive data processing algo with two main steps: state variable estimation and state variable correction
    core of kf: kalman gain...gives pred and measured different proportions of accuracy  

    Assumption:
    A = state transfer matrix from prev to now (due to time series being 1D -> use scalar KF, A = 1) 
    B = control matrix, as update of pollutant concentration not controlled by humans, thus B = 0 / not neccessary
    H = observer matrix = 1, bc 1D time series (H used to convert measured z(t) to correspond to state var x(t)-) 


    Parameters:
    measured values as np.array
    Q: Process noise cov / mean squre error matrix of process noise = error: state trans matrix A ~ actual process
    R: Measurement noise cov
    P_init: Initial estimate error cov
    x_init: Initial state estimate -> if None, use first measurement

    Returns: 
    np.array with filtered values...optimal state estimation x(t) is output by calc first pred ~ measured of k gain 
    -> optimal state estimation then corrects cov of previous process and calc iteratively obtaining filtered values
    """

    n= len(measured)
    estimates = np.zeros(n)

    #init
    x_post = measured[0] if x_init is None else x_init
    P_post = P_init

    for t in range(n):
        #PREDICTION STEP
        x_prior = x_post    #x(t)-(a priori state) = Ax(t-1) + Bu(t-1)) (u(t-1) = external control input)
        #as no external model, self-predict with current with previous 
        #actually combined with external control 
        P_prior = P_post + Q    #P(t)- = A*P(t-1)AT+Q
        #then covariance matrix of prev to now 
        #P(t)- = priori estimated cov at t and intermediate calculation result of filter

        #Kalman gain = wheter trust predicition or measure more (e.g. if pred more -> residual of (z(t) - x(t)-) less weight)
        #update K with optimal state estimate at t, 
        K = P_prior / (P_prior + R)     #K(t) = P(t)- * HT(H*P(t)-*HT +R)^-1

        #MEASUREMENT STEP
        z = measured[t] #z(t) is real measured value 
        x_post = x_prior + K * (z - x_prior)    #z(t) - x(t)- = residual of actual measurements and pred * Kalman Gain
        #x(t) = current optimal state estimate/ a posteriori as well as output of KF, x(t) = x(t)- + K(t)(z(t)-H*x(t)-)
        P_post = (1 - K) * P_prior  #P(t) = (I - K(t)*H)P(t)-
        #get noise cov at t for next iteration and uncertainty of pred reduced by updating noise dist of best estimator/updates forecast error
        #1 = Identity Matrix
        #P(t) new cov matrix to make new prediciton

        estimates[t] = x_post

    return estimates    
    