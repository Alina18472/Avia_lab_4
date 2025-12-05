
# app.py
from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from web_core import run_simulation, build_default_inputs, get_u_variable_for_equation, U_LABELS, parse_form

app = Flask(__name__)

def subscript(number):
    """Convert number to subscript string"""
    subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return str(number).translate(subscripts)

@app.template_filter('subscript')
def subscript_filter(s):
    return subscript(s)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if request.args.get('run') == '1':
            defaults = build_default_inputs()
            try:
                outputs = run_simulation(
                    defaults['u'], 
                    defaults['faks'], 
                    defaults['equations'], 
                    defaults['u_restrictions']
                )
                
                values = {
                    'u': defaults['u'],
                    'faks': defaults['faks'], 
                    'equations': defaults['equations'],
                    'u_restrictions': defaults['u_restrictions']
                }
                
                return render_template('index.html', 
                                    defaults=defaults, 
                                    values=values,
                                    ran=True, 
                                    outputs=outputs,
                                    u_labels=U_LABELS,
                                    get_u_variable_for_equation=get_u_variable_for_equation,
                                    images_b64=outputs.get('images_b64', {}),
                                    success="Модель успешно выполнена с фиксированными значениями")
            except Exception as exc:
                return render_template('index.html', 
                                    defaults=defaults, 
                                    values=None, 
                                    ran=False, 
                                    error=str(exc),
                                    u_labels=U_LABELS,
                                    get_u_variable_for_equation=get_u_variable_for_equation)
        
        defaults = build_default_inputs()
        return render_template('index.html', 
                            defaults=defaults, 
                            values=None, 
                            ran=False,
                            u_labels=U_LABELS,
                            get_u_variable_for_equation=get_u_variable_for_equation)
    
    elif request.method == 'POST':
        try:
            u, faks, equations, restrictions = parse_form(request.form)
            
            for i in range(len(u)):
                if restrictions[i] <= u[i]:
                    raise ValueError(
                        f"Предел для X{i+1} должен быть больше начального значения. "
                        f"Начальное: {u[i]:.2f}, Предел: {restrictions[i]:.2f}"
                    )
            
            # Запуск симуляции
            outputs = run_simulation(u, faks, equations, restrictions)
            
            values = {
                'u': u,
                'faks': faks, 
                'equations': equations,
                'u_restrictions': restrictions
            }
            
            return render_template('index.html', 
                                defaults=None, 
                                values=values, 
                                ran=True, 
                                outputs=outputs,
                                u_labels=U_LABELS,
                                get_u_variable_for_equation=get_u_variable_for_equation,
                                images_b64=outputs.get('images_b64', {}),
                                success="Модель успешно выполнена с пользовательскими значениями")
            
        except Exception as exc:
            defaults = build_default_inputs()
            return render_template('index.html', 
                                defaults=defaults, 
                                values=None, 
                                ran=False, 
                                error=str(exc),
                                u_labels=U_LABELS,
                                get_u_variable_for_equation=get_u_variable_for_equation)

if __name__ == '__main__':
    app.run(debug=True, port=5000)