#functions.py
import math
import numpy as np

# Линейные внешние факторы
def F1(t, params):
    a, b = params  # a + b*t
    value = a + b * t
    return max(0.1, min(1.0, value))

def F2(t, params):
    a, b = params
    value = a + b * t
    return max(0.1, min(1.0, value))

def F3(t, params):
    a, b = params
    value = a + b * t
    return max(0.1, min(1.0, value))

def F4(t, params):
    a, b = params
    value = a + b * t
    return max(0.1, min(1.0, value))

def F5(t, params):
    a, b = params
    value = a + b * t
    return max(0.1, min(1.0, value))

# Линейные функции f_i(x) = k*x + b
def fx(x, params):
    k, b = params
    result = k * x + b
    return np.clip(result, 0.05, 0.95)

# Система дифференциальных уравнений (3) из документа
def pend(u, t, factors, f):
    # u имеет 8 элементов: X1..X8
    # factors: 5 внешних факторов
    # f: 18 линейных функций f1..f18
    
    dudt = np.zeros(8)
    
    # Вычисляем внешние факторы в момент времени t
    F1_val = F1(t, factors[0])
    F2_val = F2(t, factors[1])
    F3_val = F3(t, factors[2])
    F4_val = F4(t, factors[3])
    F5_val = F5(t, factors[4])
    
    # Уравнение для X1
    dudt[0] = F3_val - fx(u[1], f[0]) * fx(u[2], f[1]) * fx(u[3], f[2])
    
    # Уравнение для X2
    dudt[1] = (F1_val + F2_val + F4_val) * fx(u[3], f[3]) * fx(u[5], f[4]) * fx(u[6], f[5]) - \
              (F3_val + F5_val) * fx(u[7], f[6])
    
    # Уравнение для X3
    dudt[2] = F4_val * fx(u[6], f[7]) - (F3_val + F5_val) * fx(u[0], f[8])
    
    # Уравнение для X4
    dudt[3] = F2_val * fx(u[1], f[9]) * fx(u[6], f[10]) - \
              (F3_val + F5_val) * fx(u[0], f[11])
    
    # Уравнение для X5
    dudt[4] = fx(u[1], f[12]) - F5_val
    
    # Уравнение для X6
    dudt[5] = F2_val * fx(u[1], f[13]) - F5_val
    
    # Уравнение для X7
    dudt[6] = F2_val * fx(u[1], f[14]) * fx(u[2], f[15]) * fx(u[3], f[16]) - \
              (F3_val + F5_val)
    
    # Уравнение для X8
    dudt[7] = F5_val - fx(u[1], f[17])
    
    # Ограничиваем скорость изменения
    return np.clip(dudt, -0.5, 0.5)