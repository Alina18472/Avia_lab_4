# web_core.py
import os
import base64
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
    from labellines import labelLines
except ImportError:
    def labelLines(*args, **kwargs):
        return None
from scipy.integrate import odeint
from scipy import interpolate
from functions import pend, F1, F2, F3, F4, F5
from radar_diagram import RadarDiagram

# Исправленные метки для 8 переменных АТС (согласно документу)
U_LABELS = [
    "X₁: Среднее количество нарушений инструкций пилотами",
    "X₂: Доля частных судов в авиации", 
    "X₃: Показатель активности органов контроля за оборотом контрафакта",
    "X₄: Количество сотрудников в метеорологических службах",
    "X₅: Катастрофы из-за метеоусловий",
    "X₆: Катастрофы из-за технических неисправностей",
    "X₇: Катастрофы из-за человеческого фактора",
    "X₈: Общее количество катастроф"
]

# Внешние факторы (линейные функции)
F_FUNCTIONS = [F1, F2, F3, F4, F5]

def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')

def smooth_data(values, window_size=5):
    if len(values) < window_size:
        return values
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(values, window, mode='same')
    half_window = window_size // 2
    for i in range(half_window):
        smoothed[i] = np.mean(values[:i*2+1])
        smoothed[-(i+1)] = np.mean(values[-(i*2+1):])
    return smoothed

def normalize_line_for_plot(values, threshold_min=0.05, threshold_max=0.95):
    if len(values) == 0:
        return values
    min_val = np.min(values)
    max_val = np.max(values)
    if min_val < 0 or max_val > 1:
        if max_val - min_val > 0:
            normalized = 0.1 + 0.8 * (values - min_val) / (max_val - min_val)
        else:
            normalized = np.full_like(values, 0.5)
        return np.clip(normalized, 0.1, 0.9)
    else:
        return values

def normalize_for_radar(values, restrictions=None):
    if len(values) == 0:
        return values
    smoothed = smooth_data(values, window_size=3)
    if restrictions is not None:
        capped_values = np.minimum(smoothed, restrictions)
        min_val = np.min(capped_values)
        max_val = np.max(capped_values)
        if max_val - min_val > 0:
            normalized = 0.05 + 0.9 * (capped_values - min_val) / (max_val - min_val)
        else:
            normalized = capped_values
        return np.clip(normalized, 0.05, 0.95)
    else:
        min_val = np.min(smoothed)
        max_val = np.max(smoothed)
        if max_val > 0.95 or min_val < 0.05:
            if max_val - min_val > 0:
                normalized = 0.05 + 0.9 * (smoothed - min_val) / (max_val - min_val)
            else:
                normalized = smoothed
            return np.clip(normalized, 0.05, 0.95)
        else:
            return smoothed

def create_smooth_line(t_original, values, num_points=1000):
    if len(t_original) < 4:
        return t_original, values
    try:
        interp_func = interpolate.interp1d(t_original, values, kind='cubic', fill_value="extrapolate")
        t_smooth = np.linspace(t_original[0], t_original[-1], num_points)
        values_smooth = interp_func(t_smooth)
        return t_smooth, values_smooth
    except:
        return t_original, values

def draw_factors(t, factors):
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Используем фиксированные названия внешних факторов из документа
    line_labels = ["F₁", "F₂", "F₃", "F₄", "F₅"]
    
    # Метки для легенды с описаниями и формулами
    legend_labels = [
        "F₁ = a + b·t",
        "F₂ = a + b·t", 
        "F₃ = a + b·t",
        "F₄ = a + b·t",
        "F₅ = a + b·t"
    ]
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Храним данные о кривых для размещения меток
    curves_data = []
    
    for i, (F_func, color, line_label) in enumerate(zip(F_FUNCTIONS, colors, line_labels)):
        y_values = []
        for v in t:
            y_values.append(F_func(v, factors[i]))
        y_values = np.array(y_values)
        
        t_smooth, y_smooth = create_smooth_line(t, y_values)
        
        # Сохраняем данные о кривой для размещения меток
        curves_data.append((t_smooth, y_smooth, color, line_label))
        
        # Рисуем линию без метки в легенде (будет отдельно)
        ax.plot(t_smooth, y_smooth, color=color, linewidth=2.5, antialiased=True, alpha=0.8)
    
    # Размещаем метки на линиях - случайно в первой половине линии
    num_curves = len(curves_data)
    
    # Генерируем случайные позиции в первой половине временного интервала
    np.random.seed(42)  # Фиксируем seed для воспроизводимости
    
    for idx, (t_curve, y_curve, color, label) in enumerate(curves_data):
        # Определяем диапазон для размещения метки (первая половина линии)
        t_min = t_curve[0]
        t_max = t_curve[0] + 0.5 * (t_curve[-1] - t_curve[0])
        
        # Выбираем случайную позицию в первой половине
        x_pos = np.random.uniform(t_min + 0.05 * (t_max - t_min), 
                                  t_max - 0.05 * (t_max - t_min))
        
        # Находим ближайшую точку на кривой
        closest_idx = np.argmin(np.abs(t_curve - x_pos))
        
        if closest_idx < len(y_curve):
            y_pos = y_curve[closest_idx]
            
            # Вычисляем угол наклона кривой в этой точке
            if closest_idx > 0 and closest_idx < len(y_curve) - 1:
                # Используем конечные разности для вычисления производной
                dy = y_curve[closest_idx + 1] - y_curve[closest_idx - 1]
                dx = t_curve[closest_idx + 1] - t_curve[closest_idx - 1]
                
                if dx != 0:
                    angle = np.degrees(np.arctan2(dy, dx))
                else:
                    angle = 90 if dy > 0 else -90
            else:
                angle = 0
            
            # Корректируем угол для лучшей читаемости
            if angle > 90:
                angle = angle - 180
            elif angle < -90:
                angle = angle + 180
            
            # Небольшое случайное смещение для избежания наложений
            offset_multiplier = np.random.uniform(0.015, 0.025)
            
            if closest_idx > 0 and closest_idx < len(y_curve) - 1:
                tx = t_curve[closest_idx + 1] - t_curve[closest_idx - 1]
                ty = y_curve[closest_idx + 1] - y_curve[closest_idx - 1]
                length = np.sqrt(tx*tx + ty*ty)
                if length > 0:
                    # Нормализованный вектор касательной
                    tx_norm = tx / length
                    ty_norm = ty / length
                    # Вектор нормали (поворот на 90 градусов)
                    nx = -ty_norm
                    ny = tx_norm
                    # Случайное смещение
                    offset_x = offset_multiplier * nx
                    offset_y = offset_multiplier * ny
                else:
                    offset_x = offset_multiplier
                    offset_y = 0
            else:
                offset_x = offset_multiplier
                offset_y = 0
            
            # Размещаем метку (более тонкая, без жирного шрифта)
            ax.text(x_pos + offset_x, y_pos + offset_y, label, 
                   color=color, fontsize=10,  # Уменьшил размер и убрал жирный
                   verticalalignment='center', 
                   horizontalalignment='center',
                   rotation=angle,
                   bbox=dict(boxstyle='round,pad=0.15',  # Уменьшил padding
                           facecolor='white', 
                           edgecolor='none', 
                           alpha=0.85))
    
    ax.set_xlabel("Время (t)")
    ax.set_ylabel("Значения")
    ax.set_title("График возмущений")
    
    # Создаем легенду с описаниями и формулами в правом верхнем углу
    from matplotlib.lines import Line2D
    legend_elements = []
    for i in range(len(legend_labels)):
        legend_elements.append(Line2D([0], [0], color=colors[i], lw=2, label=legend_labels[i]))
    
    # Легенда в правом верхнем углу
    ax.legend(handles=legend_elements, fontsize=8, loc='upper right')
    
    ax.grid(True, alpha=0.3)
    
    # Устанавливаем диапазон 0-1
    ax.set_ylim(0, 1.0)
    
    # Добавляем горизонтальную линию на уровне 1 для ориентира
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3, linewidth=0.5)
    
    plt.tight_layout()
    return fig

def create_graphics(t, data, factors):
    figs_b64 = []
    
    # Словарь для нижних индексов
    subscript_numbers = {
        1: '₁', 2: '₂', 3: '₃', 4: '₄', 5: '₅', 6: '₆', 7: '₇', 8: '₈'
    }
    
    # Нормализация данных для отображения
    normalized_data = np.zeros_like(data)
    for i in range(8):
        y_data = np.maximum(0.01, data[:, i])
        normalized_data[:, i] = normalize_line_for_plot(y_data)
    
    # СОЗДАЕМ ДВА ГРАФИКА В СТОЛБИК
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # Цвета для графиков
    colors1 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Первые 4 характеристики
    colors2 = ['#9467bd', '#8c564b', '#e377c2', '#7f7f7f']  # Последние 4 характеристики
    
    # ПЕРВЫЙ ГРАФИК: характеристики X1-X4
    for i in range(4):
        y_data = normalized_data[:, i]
        label = f"X{subscript_numbers[i+1]}"
        ax1.plot(t, y_data, color=colors1[i], label=label, linewidth=2.0, antialiased=True, alpha=0.8)
    
    ax1.set_xlabel("Время (t)")
    ax1.set_ylabel("Значения характеристик")
    ax1.set_title("Характеристики X₁–X₄")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.0)
    
    # Исправленная легенда для первого графика - используем метки характеристик
    legend_labels1 = [
        "X₁: Среднее количество нарушений инструкций пилотами",
        "X₂: Доля частных судов в авиации", 
        "X₃: Показатель активности органов контроля",
        "X₄: Количество сотрудников в метеослужбах"
    ]
    ax1.legend(legend_labels1, fontsize=8, loc='upper right')
    
    # ВТОРОЙ ГРАФИК: характеристики X5-X8
    for i in range(4, 8):
        y_data = normalized_data[:, i]
        label = f"X{subscript_numbers[i+1]}"
        ax2.plot(t, y_data, color=colors2[i-4], label=label, linewidth=2.0, antialiased=True, alpha=0.8)
    
    ax2.set_xlabel("Время (t)")
    ax2.set_ylabel("Значения характеристик")
    ax2.set_title("Характеристики X₅–X₈")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.0)
    
    # Исправленная легенда для второго графика - используем метки характеристик
    legend_labels2 = [
        "X₅: Катастрофы из-за метеоусловий",
        "X₆: Катастрофы из-за технических неисправностей",
        "X₇: Катастрофы из-за человеческого фактора",
        "X₈: Общее количество катастроф"
    ]
    ax2.legend(legend_labels2, fontsize=8, loc='upper right')
    
    plt.tight_layout()
    figs_b64.append(_fig_to_base64(fig1))
    plt.close(fig1)
    
    # График внешних факторов (оставляем без изменений)
    fig2 = draw_factors(t, factors)
    figs_b64.append(_fig_to_base64(fig2))
    plt.close(fig2)
    
    return figs_b64

def draw_radar_series(data, initial_equations, restrictions):
    radar = RadarDiagram()
    imgs = []
    normalized_initial = normalize_for_radar(np.array(initial_equations), restrictions)
    time_points = [int(len(data) / 4), int(len(data) / 2), int(len(data) * 3 / 4), -1]
    normalized_points = []
    for point_idx in time_points:
        point_data = data[point_idx, :]
        normalized_point = normalize_for_radar(point_data, restrictions)
        normalized_points.append(normalized_point)
    labels = [f"X$_{i+1}$" for i in range(8)]
    titles = [
        "Характеристики системы в начальный момент времени",
        "Характеристики системы при t=0.25",
        "Характеристики системы при t=0.5",
        "Характеристики системы при t=0.75",
        "Характеристики системы при t=1"
    ]
    imgs.append(base64.b64encode(radar.draw_bytes(normalized_initial, labels, titles[0], restrictions, normalized_initial)).decode('ascii'))
    for i, pt in enumerate(normalized_points):
        imgs.append(base64.b64encode(radar.draw_bytes(pt, labels, titles[i+1], restrictions, normalized_initial)).decode('ascii'))
    return imgs

def run_simulation(initial_equations, factors, equations, restrictions):
    # Убедимся, что initial_equations имеет 8 элементов
    init_eq = np.array(initial_equations[:8], dtype=float)
    
    # Добавим небольшой шум для устойчивости
    noise = np.random.uniform(-0.05, 0.05, size=8)
    init_eq = np.clip(init_eq + noise, 0.01, 0.99)
    
    # Временной интервал 0-1 (нормированные годы от 2011 до 2025)
    t = np.linspace(0, 1, 50)
    
    # Решение системы уравнений
    data_sol = odeint(pend, init_eq, t, args=(factors, equations))
    data_sol = np.maximum(data_sol, 0)
    
    # Создание графиков
    figure_b64 = create_graphics(t, data_sol, factors)
    
    # Создание радарных диаграмм
    radar_imgs = draw_radar_series(data_sol, initial_equations[:8], restrictions[:8])
    
    return {
        'images_b64': {
            'figure1': figure_b64[0],
            'figure2': figure_b64[1],
            'diagram1': radar_imgs[0],
            'diagram2': radar_imgs[1],
            'diagram3': radar_imgs[2],
            'diagram4': radar_imgs[3],
            'diagram5': radar_imgs[4],
        },
    }

def build_default_inputs():
    """Создает фиксированные входные данные (старая версия)"""
    # Начальные значения для 8 переменных АТС
    u_values = [0.5, 0.6, 0.4, 0.55, 0.3, 0.35, 0.45, 0.25]
    
    # Ограничения
    u_restrictions = [0.9, 0.95, 0.85, 0.9, 0.7, 0.75, 0.8, 0.6]
    
    # 5 внешних факторов - ФИКСИРОВАННЫЕ значения
    fixed_factors = [
        [0.63, 0.37],    # F1: Средняя выработка ресурса до списания
        [1.00, -0.23],   # F2: Доля иностранных воздушных судов
        [1.00, -0.33],   # F3: Средний лётный стаж пилотов
        [0.51, 0.46],    # F4: Стоимость авиационного топлива 
        [0.60, 0.40]     # F5: Количество нормативно-правовых актов
    ]
    
    # 18 уравнений f1-f18 - ФИКСИРОВАННЫЕ коэффициенты
    fixed_equations = [
        [-0.49, 0.97],   # f1(X2) = 0,97 - 0,49*X2
        [0.10, 0.53],    # f2(X3) = 0,53 + 0,1*X3
        [0.06, 0.53],    # f3(X4) = 0,53 + 0,06*X4
        [0.08, 0.75],    # f4(X4) = 0,75 + 0,08*X4
        [0.20, 0.72],    # f5(X6) = 0,72 + 0,2*X6
        [-0.20, 0.97],   # f6(X7) = 0,97 - 0,2*X7
        [0.38, 0.52],    # f7(X8) = 0,52 + 0,38*X8
        [-0.37, 0.78],   # f8(X7) = 0,78 - 0,37*X7
        [0.09, 0.45],    # f9(X1) = 0,45 + 0,09*X1
        [0.17, 0.55],    # f10(X2) = 0,55 + 0,17*X2
        [-0.44, 1.02],   # f11(X7) = 1,02 - 0,44*X7
        [0.05, 0.66],    # f12(X1) = 0,66 + 0,05*X1
        [0.48, 0.45],    # f13(X2) = 0,45 + 0,48*X2
        [-0.47, 1.18],   # f14(X2) = 1,18 - 0,47*X2
        [-0.77, 1.37],   # f15(X2) = 1,37 - 0,77*X2
        [0.22, 0.59],    # f16(X3) = 0,59 + 0,22*X3
        [-0.71, 1.24],   # f17(X4) = 1,24 - 0,71*X4
        [-0.02, 0.87]    # f18(X2) = 0,87 - 0,02*X2
    ]
    
    defaults = {
        'u': [round(x, 2) for x in u_values],
        'u_restrictions': [round(x, 2) for x in u_restrictions],
        'faks': [[round(float(factor[0]), 2), round(float(factor[1]), 2)] for factor in fixed_factors],
        'equations': [[round(float(eq[0]), 2), round(float(eq[1]), 2)] for eq in fixed_equations]
    }
    
    return defaults

def build_random_inputs():
    """Создает случайные входные данные в диапазоне [0,1]"""
    rng = np.random.default_rng()
    
    # Начальные значения для 8 переменных АТС
    u_values = [
        round(rng.uniform(0.1, 0.9), 2) for _ in range(8)
    ]
    
    # Ограничения - всегда больше начальных значений
    u_restrictions = []
    for i in range(8):
        min_val = min(u_values[i] + 0.05, 0.95)  # Гарантируем, что ограничение больше начального значения
        restriction = round(rng.uniform(min_val, 1.0), 2)
        u_restrictions.append(min(restriction, 1.0))  # Не превышаем 1.0
    
    # 5 внешних факторов (возмущений) - случайные в диапазоне [0,1]
    # Каждый фактор: [свободный член, коэффициент при t]
    faks = []
    for _ in range(5):
        a = round(rng.uniform(0.0, 1.0), 2)  # свободный член
        b = round(rng.uniform(-0.5, 0.5), 2)  # коэффициент при t
        faks.append([a, b])
    
    # 18 уравнений характеристик - случайные коэффициенты в диапазоне
    equations = []
    for _ in range(18):
        k = round(rng.uniform(-1.0, 1.0), 2)  # коэффициент k
        b = round(rng.uniform(0.0, 1.0), 2)   # свободный член b
        equations.append([k, b])
    
    return {
        'u': u_values,
        'u_restrictions': u_restrictions,
        'faks': faks,
        'equations': equations
    }

def get_u_variable_for_equation(equation_number):
    # Маппинг уравнений f1-f18 на переменные X1-X8
    mapping = {
        1: 2,   # f1 зависит от X2
        2: 3,   # f2 зависит от X3
        3: 4,   # f3 зависит от X4
        4: 4,   # f4 зависит от X4
        5: 6,   # f5 зависит от X6
        6: 7,   # f6 зависит от X7
        7: 8,   # f7 зависит от X8
        8: 7,   # f8 зависит от X7
        9: 1,   # f9 зависит от X1
        10: 2,  # f10 зависит от X2
        11: 7,  # f11 зависит от X7
        12: 1,  # f12 зависит от X1
        13: 2,  # f13 зависит от X2
        14: 2,  # f14 зависит от X2
        15: 2,  # f15 зависит от X2
        16: 3,  # f16 зависит от X3
        17: 4,  # f17 зависит от X4
        18: 2   # f18 зависит от X2
    }
    return mapping.get(equation_number, "?")

def parse_form(form):
    u = []
    u_restrictions = []
    
    # Считываем 8 начальных значений
    for i in range(1, 9):
        field_name = f'u{i}'
        value = form.get(field_name, '0.5')
        try:
            u.append(float(value or 0.5))
        except ValueError:
            u.append(0.5)
        
        # Ограничения
        restriction_field = f'u_restrictions{i}'
        restriction_value = form.get(restriction_field, '1.0')
        try:
            u_restrictions.append(float(restriction_value or 1.0))
        except ValueError:
            u_restrictions.append(1.0)
    
    # 5 внешних факторов - считываем пользовательский ввод
    factors = []
    for i in range(1, 6):
        a_field = f'fak{i}_a'
        b_field = f'fak{i}_b'
        
        a_value = form.get(a_field, '0.5')
        b_value = form.get(b_field, '0.0')
        
        try:
            a = float(a_value or 0.5)
        except ValueError:
            a = 0.5
        
        try:
            b = float(b_value or 0.0)
        except ValueError:
            b = 0.0
        
        # Ограничиваем значения [0,1]
        a = max(0.0, min(1.0, a))
        b = max(-1.0, min(1.0, b))
        
        factors.append([a, b])
    
    # 18 уравнений f1-f18 - считываем пользовательский ввод
    equations = []
    for i in range(1, 19):
        k_field = f'f{i}_k'
        b_field = f'f{i}_b'
        
        k_value = form.get(k_field, '0.5')
        b_value = form.get(b_field, '0.5')
        
        try:
            k = float(k_value or 0.5)
        except ValueError:
            k = 0.5
        
        try:
            b = float(b_value or 0.5)
        except ValueError:
            b = 0.5
        
        # Ограничиваем значения
        k = max(-1.0, min(1.0, k))
        b = max(0.0, min(1.0, b))
        
        equations.append([k, b])
    
    return u[:8], factors[:5], equations[:18], u_restrictions[:8]