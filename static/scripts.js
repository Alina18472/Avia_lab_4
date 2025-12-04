
// scripts.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Модель АТС: Инициализация интерфейса...');
    
    // ==================== ИНИЦИАЛИЗАЦИЯ ВКЛАДОК ====================
    function initTabs() {
        console.log('Инициализация вкладок...');
        const tabs = document.querySelectorAll('.nav-link');
        const tabContents = document.querySelectorAll('.tab-content');
        
        function switchTab(tabName) {
            // Скрыть все вкладки
            tabContents.forEach(content => {
                content.style.display = 'none';
                content.classList.remove('active');
            });
            
            // Убрать активный класс со всех вкладок
            tabs.forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Показать выбранную вкладку
            const activeTab = document.getElementById(tabName + '-tab');
            if (activeTab) {
                activeTab.style.display = 'block';
                activeTab.classList.add('active');
            }
            
            // Добавить активный класс выбранной вкладке
            const activeLink = document.querySelector(`.nav-link[data-tab="${tabName}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
        
        // Обработчики кликов по вкладкам
        tabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                const tabName = this.getAttribute('data-tab');
                switchTab(tabName);
            });
        });
        
        // Кнопки перехода к параметрам
        document.querySelectorAll('.switch-to-params-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                switchTab('params');
            });
        });
        
        // Показываем первую вкладку по умолчанию
        switchTab('params');
    }
    
    // ==================== УБИРАЕМ ДИАЛОГ ПРИ ПЕРЕЗАГРУЗКЕ ====================
    window.addEventListener('beforeunload', function(e) {
        delete e['returnValue'];
    });
    
    // Конфигурация - ТОЛЬКО ПОЛОЖИТЕЛЬНЫЕ значения в диапазоне [0, 1]
    const CONFIG = {
        ABSOLUTE_MIN: 0.0,     // минимальное возможное значение
        ABSOLUTE_MAX: 1.0,     // максимальное возможное значение
        DECIMALS: 2            // знаков после запятой
    };
    
    // Утилиты
    const Utils = {
        parseNumber: function(str) {
            if (!str || str.trim() === '') return NaN;
            // Заменяем запятую на точку для парсинга
            return parseFloat(str.replace(',', '.'));
        },
        
        formatNumber: function(num) {
            if (isNaN(num)) return '0.00';
            // Округляем до 2 знаков после запятой
            return Math.round(num * 100) / 100;
        },
        
        clampValue: function(value) {
            if (isNaN(value)) return 0.5;
            // Ограничиваем между 0 и 1
            const clamped = Math.max(CONFIG.ABSOLUTE_MIN, Math.min(CONFIG.ABSOLUTE_MAX, value));
            return this.formatNumber(clamped);
        },
        
        // Генерация случайного числа ТОЛЬКО в диапазоне [0, 1]
        getRandomNumber: function(min = 0.0, max = 1.0) {
            min = Math.max(0.0, min);
            max = Math.min(1.0, max);
            return this.formatNumber(Math.random() * (max - min) + min);
        },
        
        // Проверка на положительное число в диапазоне [0, 1]
        isValidPositive: function(value) {
            if (isNaN(value)) return false;
            return value >= 0.0 && value <= 1.0;
        }
    };
    
    // Валидатор - проверяем ТОЛЬКО положительные значения [0, 1]
    const Validator = {
        validateInput: function(input) {
            const value = Utils.parseNumber(input.value);
            
            if (!Utils.isValidPositive(value)) {
                input.classList.add('invalid');
                return false;
            } else {
                input.classList.remove('invalid');
                
                // Автоматически корректируем значение в диапазоне [0, 1]
                const corrected = Utils.clampValue(value);
                input.value = corrected.toFixed(2);
                
                return true;
            }
        },
        
        validateAll: function() {
            let isValid = true;
            const inputs = document.querySelectorAll('input[type="text"]:not(#status-input)');
            
            inputs.forEach(input => {
                if (!this.validateInput(input)) {
                    isValid = false;
                }
                
                // Дополнительная проверка на ограничения
                if (input.name.startsWith('u_restrictions')) {
                    const num = input.name.replace('u_restrictions', '');
                    const initialInput = document.querySelector(`input[name="u${num}"]`);
                    
                    if (initialInput) {
                        const initialValue = Utils.parseNumber(initialInput.value);
                        const limitValue = Utils.parseNumber(input.value);
                        
                        if (Utils.isValidPositive(initialValue) && Utils.isValidPositive(limitValue)) {
                            if (limitValue <= initialValue) {
                                input.classList.add('invalid-limit');
                                isValid = false;
                            } else {
                                input.classList.remove('invalid-limit');
                            }
                        }
                    }
                }
            });
            
            return isValid;
        }
    };
    
    // Функция сохранения в localStorage
    function saveToStorage() {
        const formData = {};
        const inputs = document.querySelectorAll('input[type="text"]:not(#status-input)');
        
        inputs.forEach(input => {
            if (input.name) {
                formData[input.name] = input.value;
            }
        });
        
        localStorage.setItem('ats_form_data', JSON.stringify(formData));
    }
    
    // Загрузка сохраненных данных
    function loadFromStorage() {
        const savedData = localStorage.getItem('ats_form_data');
        if (savedData) {
            try {
                const formData = JSON.parse(savedData);
                
                Object.keys(formData).forEach(name => {
                    const input = document.querySelector(`input[name="${name}"]`);
                    if (input && input.type === 'text' && input.id !== 'status-input') {
                        const value = Utils.parseNumber(formData[name]);
                        if (Utils.isValidPositive(value)) {
                            input.value = Utils.clampValue(value).toFixed(2);
                        }
                    }
                });
                
                console.log('Данные загружены из localStorage');
            } catch (e) {
                console.error('Ошибка загрузки:', e);
            }
        }
    }
    
    // Инициализация интерфейса
    function initInterface() {
        console.log('Инициализация интерфейса...');
        
        // Инициализация вкладок
        initTabs();
        
        // ==================== ПОЛЕ СТАТУСА ====================
        const statusInput = document.getElementById('status-input');
        if (statusInput) {
            statusInput.type = 'text';
            statusInput.readOnly = true;
            statusInput.value = 'Готов к расчетам';
            
            // Блокируем ввод
            statusInput.addEventListener('keydown', function(e) {
                e.preventDefault();
                return false;
            });
            
            statusInput.addEventListener('input', function(e) {
                this.value = 'Готов к расчетам';
            });
            
            // Визуальные настройки
            statusInput.style.userSelect = 'none';
            statusInput.style.cursor = 'default';
        }
        
        // ==================== НАСТРОЙКА ПОЛЕЙ ВВОДА ====================
        const inputs = document.querySelectorAll('input[type="text"]:not(#status-input)');
        
        inputs.forEach(input => {
            // Разрешаем ввод ТОЛЬКО цифр и точки/запятой
            input.addEventListener('keypress', function(e) {
                // Разрешаем: цифры, точка, запятая
                const allowedChars = /[0-9.,]/;
                const key = String.fromCharCode(e.keyCode || e.which);
                
                if (e.key === 'Enter') return; // Разрешаем Enter
                
                if (!allowedChars.test(key) && key !== 'Enter') {
                    e.preventDefault();
                }
            });
            
            // Обработка ввода - очищаем класс ошибки
            input.addEventListener('input', function() {
                this.classList.remove('invalid', 'invalid-limit');
            });
            
            // При потере фокуса - проверяем и корректируем
            input.addEventListener('blur', function() {
                Validator.validateInput(this);
                saveToStorage();
            });
            
            // Разрешаем вставку
            input.addEventListener('paste', function(e) {
                setTimeout(() => {
                    Validator.validateInput(this);
                }, 10);
            });
        });
        
        // ==================== СЛУЧАЙНОЕ ЗАПОЛНЕНИЕ ====================
        const randomBtn = document.getElementById('random-fill-btn');
        if (randomBtn) {
            randomBtn.addEventListener('click', function() {
                console.log('Случайное заполнение - ТОЛЬКО положительные значения [0, 1]');
                
                // 1. u1-u8 (от 0.1 до 0.9)
                for (let i = 1; i <= 8; i++) {
                    const input = document.querySelector(`input[name="u${i}"]`);
                    if (input) {
                        input.value = Utils.getRandomNumber(0.1, 0.9);
                    }
                }
                
                // 2. u_restrictions1-8 (всегда больше начальных значений, но не больше 1.0)
                for (let i = 1; i <= 8; i++) {
                    const initialInput = document.querySelector(`input[name="u${i}"]`);
                    const limitInput = document.querySelector(`input[name="u_restrictions${i}"]`);
                    
                    if (initialInput && limitInput) {
                        const initialValue = Utils.parseNumber(initialInput.value);
                        if (!isNaN(initialValue)) {
                            // Ограничение должно быть больше начального значения, но не больше 1.0
                            const minLimit = Math.min(initialValue + 0.05, 0.99);
                            const maxLimit = 1.0;
                            limitInput.value = Utils.getRandomNumber(minLimit, maxLimit);
                        }
                    }
                }
                
                // 3. fak1_a - fak5_a (от 0.0 до 1.0)
                // fak1_b - fak5_b (от 0.0 до 0.5) - ТОЛЬКО ПОЛОЖИТЕЛЬНЫЕ коэффициенты
                for (let i = 1; i <= 5; i++) {
                    const aInput = document.querySelector(`input[name="fak${i}_a"]`);
                    const bInput = document.querySelector(`input[name="fak${i}_b"]`);
                    
                    if (aInput) {
                        aInput.value = Utils.getRandomNumber(0.0, 1.0);
                    }
                    if (bInput) {
                        // ТОЛЬКО ПОЛОЖИТЕЛЬНЫЕ коэффициенты для линейных функций
                        bInput.value = Utils.getRandomNumber(0.0, 0.5);
                    }
                }
                
                // 4. f1_k - f18_k (от 0.0 до 1.0) и f1_b - f18_b (от 0.0 до 1.0)
                // ТОЛЬКО ПОЛОЖИТЕЛЬНЫЕ коэффициенты
                for (let i = 1; i <= 18; i++) {
                    const kInput = document.querySelector(`input[name="f${i}_k"]`);
                    const bInput = document.querySelector(`input[name="f${i}_b"]`);
                    
                    if (kInput) {
                        kInput.value = Utils.getRandomNumber(0.0, 1.0);
                    }
                    if (bInput) {
                        bInput.value = Utils.getRandomNumber(0.0, 1.0);
                    }
                }
                
                // Валидируем все значения
                Validator.validateAll();
                
                // Сохраняем случайные значения
                saveToStorage();
                
                // Обновляем статус
                if (statusInput) {
                    statusInput.value = 'Заполнено случайными значениями';
                    statusInput.style.color = '#2196F3';
                }
            });
        }
        
        // ==================== КНОПКА ОЧИСТКИ ====================
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', function() {
                console.log('Очистка формы');
                
                const inputs = document.querySelectorAll('input[type="text"]:not(#status-input)');
                inputs.forEach(input => {
                    // Устанавливаем безопасные положительные значения по умолчанию
                    if (input.name.startsWith('u')) {
                        input.value = '0.50';
                    } else if (input.name.startsWith('u_restrictions')) {
                        input.value = '0.80';
                    } else if (input.name.startsWith('fak') && input.name.endsWith('_a')) {
                        input.value = '0.50';
                    } else if (input.name.startsWith('fak') && input.name.endsWith('_b')) {
                        input.value = '0.10'; // Положительный коэффициент
                    } else if (input.name.startsWith('f') && input.name.endsWith('_k')) {
                        input.value = '0.50';
                    } else if (input.name.startsWith('f') && input.name.endsWith('_b')) {
                        input.value = '0.50';
                    }
                    
                    // Очищаем классы ошибок
                    input.classList.remove('invalid', 'invalid-limit');
                });
                
                if (statusInput) {
                    statusInput.value = 'Форма очищена';
                    statusInput.style.color = '#4CAF50';
                    setTimeout(() => {
                        statusInput.value = 'Готов к расчетам';
                        statusInput.style.color = '';
                    }, 2000);
                }
                
                localStorage.removeItem('ats_form_data');
            });
        }
        
        // ==================== КНОПКА ВЫЧИСЛЕНИЯ ====================
        const calculateBtn = document.getElementById('calculate-btn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', function(e) {
                // 1. Валидируем все поля
                if (!Validator.validateAll()) {
                    e.preventDefault();
                    
                    // Показываем ошибки
                    const invalidInputs = document.querySelectorAll('.invalid, .invalid-limit');
                    let errorMessage = 'Пожалуйста, исправьте ошибки:\n\n';
                    
                    invalidInputs.forEach((input, index) => {
                        if (index < 5) { // Показываем только первые 5 ошибок
                            const fieldName = input.name;
                            if (input.classList.contains('invalid')) {
                                errorMessage += `- Поле "${fieldName}" должно содержать число от 0.00 до 1.00\n`;
                            }
                            if (input.classList.contains('invalid-limit')) {
                                const num = fieldName.replace('u_restrictions', '');
                                errorMessage += `- Предельное значение для X${num} должно быть БОЛЬШЕ начального\n`;
                            }
                        }
                    });
                    
                    if (invalidInputs.length > 0) {
                        if (statusInput) {
                            statusInput.value = 'Ошибка: значения должны быть от 0 до 1';
                            statusInput.style.color = '#f44336';
                        }
                        
                        alert(errorMessage + '\n\nВсе значения должны быть в диапазоне от 0.00 до 1.00');
                        return;
                    }
                }
                
                // 2. Обновляем статус
                if (statusInput) {
                    statusInput.value = 'Вычисление...';
                    statusInput.style.color = '#ff9800';
                }
                
                // 3. Сохраняем данные
                saveToStorage();
                
                // 4. Форма отправляется обычным способом
                console.log('Форма отправляется...');
            });
        }
        
        // ==================== ЗАГРУЗКА СОХРАНЕННЫХ ДАННЫХ ====================
        loadFromStorage();
        
        // ==================== АВТОСОХРАНЕНИЕ ПРИ ПЕРЕКЛЮЧЕНИИ ВКЛАДОК ====================
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.addEventListener('click', function() {
                saveToStorage();
            });
        });
        
        console.log('Интерфейс инициализирован');
    }
    
    // ==================== CSS ДЛЯ ВИЗУАЛЬНЫХ ИНДИКАТОРОВ ====================
    const style = document.createElement('style');
    style.textContent = `
        .invalid {
            border: 2px solid #f44336 !important;
            background-color: #ffebee !important;
        }
        
        .invalid-limit {
            border: 2px solid #ff9800 !important;
            background-color: #fff3e0 !important;
        }
        
        input:focus {
            border-color: #2196F3 !important;
            box-shadow: 0 0 5px rgba(33, 150, 243, 0.3) !important;
            outline: none !important;
        }
        
        .status-ready {
            color: #4CAF50 !important;
            font-weight: bold !important;
        }
        
        .input-group input {
            transition: all 0.3s ease;
        }
       
    `;
    document.head.appendChild(style);
    
    // ==================== ЗАПУСК ====================
    initInterface();
    
    // ==================== ОБРАБОТКА СОБЫТИЙ БРАУЗЕРА ====================
    window.addEventListener('pageshow', function(event) {
        // Восстанавливаем статус при возврате на страницу
        const statusInput = document.getElementById('status-input');
        if (statusInput && statusInput.value === 'Вычисление...') {
            statusInput.value = 'Готов к расчетам';
            statusInput.style.color = '';
        }
    });
    
    console.log('Модель АТС полностью инициализирована');
});