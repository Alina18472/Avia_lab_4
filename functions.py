
import numpy as np

def F1(t, fak):
    val = fak[0] + fak[1] * t
    return np.clip(val, 0.0, 1.0)

def F2(t, fak):
    val = fak[0] + fak[1] * t
    return np.clip(val, 0.0, 1.0)

def F3(t, fak):
    val = fak[0] + fak[1] * t
    return np.clip(val, 0.0, 1.0)

def F4(t, fak):
    val = fak[0] + fak[1] * t
    return np.clip(val, 0.0, 1.0)

def F5(t, fak):
    val = fak[0] + fak[1] * t
    return np.clip(val, 0.0, 1.0)

def f1(X2, eq):
    val = eq[1] + eq[0] * X2
    return np.clip(val, 0.0, 1.0)

def f2(X3, eq):
    val = eq[1] + eq[0] * X3
    return np.clip(val, 0.0, 1.0)

def f3(X4, eq):
    val = eq[1] + eq[0] * X4
    return np.clip(val, 0.0, 1.0)

def f4(X4, eq):
    val = eq[1] + eq[0] * X4
    return np.clip(val, 0.0, 1.0)

def f5(X6, eq):
    val = eq[1] + eq[0] * X6
    return np.clip(val, 0.0, 1.0)

def f6(X7, eq):
    val = eq[1] + eq[0] * X7
    return np.clip(val, 0.0, 1.0)

def f7(X8, eq):
    val = eq[1] + eq[0] * X8
    return np.clip(val, 0.0, 1.0)

def f8(X7, eq):
    val = eq[1] + eq[0] * X7
    return np.clip(val, 0.0, 1.0)

def f9(X1, eq):
    val = eq[1] + eq[0] * X1
    return np.clip(val, 0.0, 1.0)

def f10(X2, eq):
    val = eq[1] + eq[0] * X2
    return np.clip(val, 0.0, 1.0)

def f11(X7, eq):
    val = eq[1] + eq[0] * X7
    return np.clip(val, 0.0, 1.0)

def f12(X1, eq):
    val = eq[1] + eq[0] * X1
    return np.clip(val, 0.0, 1.0)

def f13(X2, eq):
    val = eq[1] + eq[0] * X2
    return np.clip(val, 0.0, 1.0)

def f14(X2, eq):
    val = eq[1] + eq[0] * X2
    return np.clip(val, 0.0, 1.0)

def f15(X2, eq):
    val = eq[1] + eq[0] * X2
    return np.clip(val, 0.0, 1.0)

def f16(X3, eq):
    val = eq[1] + eq[0] * X3
    return np.clip(val, 0.0, 1.0)

def f17(X4, eq):
    val = eq[1] + eq[0] * X4
    return np.clip(val, 0.0, 1.0)

def f18(X2, eq):
    val = eq[1] + eq[0] * X2
    return np.clip(val, 0.0, 1.0)

def pend(y, t, factors, equations):
    dydt = np.zeros(8)
    
    F_values = []
    F_functions = [F1, F2, F3, F4, F5]
    for i in range(5):
        f_val = F_functions[i](t, factors[i])
        F_values.append(np.clip(f_val, 0.0, 1.0))
    
    dydt[0] = F_values[0] * (f1(y[1], equations[0]) - y[0])
    
    dydt[1] = F_values[1] * (f2(y[2], equations[1]) - y[1])
    
    dydt[2] = F_values[2] * (f3(y[3], equations[2]) - y[2])
    
    dydt[3] = F_values[3] * (f4(y[3], equations[3]) - y[3])
    
    dydt[4] = f5(y[5], equations[4]) * f6(y[6], equations[5]) * 0.8
    
    dydt[5] = f7(y[7], equations[6]) * f8(y[6], equations[7]) * 0.8
    
    dydt[6] = f9(y[0], equations[8]) * f10(y[1], equations[9]) * f11(y[6], equations[10]) * 0.6
    
    product = 1.0
    for j in range(11, 18):
        if j == 11: 
            product *= f12(y[0], equations[j])
        elif j == 12: 
            product *= f13(y[1], equations[j])
        elif j == 13:
            product *= f14(y[1], equations[j])
        elif j == 14: 
            product *= f15(y[1], equations[j])
        elif j == 15: 
            product *= f16(y[2], equations[j])
        elif j == 16:  
            product *= f17(y[3], equations[j])
        elif j == 17:  
            product *= f18(y[1], equations[j])
    
    dydt[7] = product * 0.5
    
    dydt = np.clip(dydt, -0.8, 0.8)
    
    return dydt