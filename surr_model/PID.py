"""
PID controller implementation within MEDEAS
Wrote by Noe Diffels
November 2024
"""

"""
The idea:

is to control Load shedding, which can be decreased when:
    - RES capacity installed increases
    - Storage capacity installed increases
    - NTC increases
All these capacities depends on the grid investments. 

is to control curtailment, which can be decreased when:
    - Storage capacity installed increases (Previous work's error, curtailment increase when storage increase. See Section 2.3.5 for further explanations)
    - NTC increases 
All these capacities depends on the grid investments. 


"""

import numpy as np

"""
The function below calculates the value of the control variable (u(t)) based on the measured 
value and setpoint value. The function also accepts parameters of the controller.
"""

def PID(Kp, Ki, Kd, time, time_prev, setpoint, measurement):
    global I, e_prev
    if time == 1995:
        I = 0
        e_prev = 0

    # Value of offset - when the error is equal zero. Set to 1%.
    # It means that the controller try to converge the targets to 1%.

    # offset = 0.01
    
    # Error e(t)
    e = abs(setpoint - measurement) # Ouput u(t) should be > 0, thus using abs().
    
    # P-I-D
    P = Kp*e
    I = I + Ki*e*(time - time_prev)
    D = Kd*(e - e_prev)/(time - time_prev)

    e_prev = e
    # calculate control variable - u(t): grid investments
    # u = offset + P + I + D
    u = P + I + D

    # Since this problem is asymmetric (investments can not be negative), 
    # positive constraints is implemented. 
    if u <= 0:
        #print("PID control is negative, investments set to 0.")
        return 0
    else:
        return u