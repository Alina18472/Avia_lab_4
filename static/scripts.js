
// scripts.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Модель АТС: Инициализация интерфейса...');

    function initTabs() {
        console.log('Инициализация вкладок...');
        const tabs = document.querySelectorAll('.nav-link');
        const tabContents = document.querySelectorAll('.tab-content');
        
        function switchTab(tabName) {
            tabContents.forEach(content => {
                content.style.display = 'none';
                content.classList.remove('active');
            });
          
            tabs.forEach(tab => {
                tab.classList.remove('active');
            });
           
            const activeTab = document.getElementById(tabName + '-tab');
            if (activeTab) {
                activeTab.style.display = 'block';
                activeTab.classList.add('active');
            }
            
            const activeLink = document.querySelector(`.nav-link[data-tab="${tabName}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
        
        tabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                const tabName = this.getAttribute('data-tab');
                switchTab(tabName);
            });
        });
        
        document.querySelectorAll('.switch-to-params-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                switchTab('params');
            });
        });
        
        switchTab('params');
    }
    
    window.addEventListener('beforeunload', function(e) {
        delete e['returnValue'];
    });
    
    const CONFIG = {
        ABSOLUTE_MIN: 0.0,     
        ABSOLUTE_MAX: 1.0,     
        DECIMALS: 2           
    };
    
    const Utils = {
        parseNumber: function(str) {
            if (!str || str.trim() === '') return NaN;
            return parseFloat(str.replace(',', '.'));
        },
        
        formatNumber: function(num) {
            if (isNaN(num)) return '0.00';
            return Math.round(num * 100) / 100;
        },
        
        clampValue: function(value) {
            if (isNaN(value)) return 0.5;
            const clamped = Math.max(CONFIG.ABSOLUTE_MIN, Math.min(CONFIG.ABSOLUTE_MAX, value));
            return this.formatNumber(clamped);
        },
        
        getRandomNumber: function(min = 0.0, max = 1.0) {
            min = Math.max(0.0, min);
            max = Math.min(1.0, max);
            return this.formatNumber(Math.random() * (max - min) + min);
        },
        
        isValidPositive: function(value) {
            if (isNaN(value)) return false;
            return value >= 0.0 && value <= 1.0;
        }
    };

    const Validator = {
        validateInput: function(input) {
            const value = Utils.parseNumber(input.value);
            
            if (!Utils.isValidPositive(value)) {
                input.classList.add('invalid');
                return false;
            } else {
                input.classList.remove('invalid');
                
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
    
    function initInterface() {
        console.log('Инициализация интерфейса...');
        
        initTabs();
        
        const statusInput = document.getElementById('status-input');
        if (statusInput) {
            statusInput.type = 'text';
            statusInput.readOnly = true;
            statusInput.value = 'Готов к расчетам';
            
            statusInput.addEventListener('keydown', function(e) {
                e.preventDefault();
                return false;
            });
            
            statusInput.addEventListener('input', function(e) {
                this.value = 'Готов к расчетам';
            });
            
            statusInput.style.userSelect = 'none';
            statusInput.style.cursor = 'default';
        }
        
        const inputs = document.querySelectorAll('input[type="text"]:not(#status-input)');
        
        inputs.forEach(input => {
            input.addEventListener('keypress', function(e) {
             
                const allowedChars = /[0-9.,]/;
                const key = String.fromCharCode(e.keyCode || e.which);
                
                if (e.key === 'Enter') return; 
                
                if (!allowedChars.test(key) && key !== 'Enter') {
                    e.preventDefault();
                }
            });
            
            input.addEventListener('input', function() {
                this.classList.remove('invalid', 'invalid-limit');
            });
            
            input.addEventListener('blur', function() {
                Validator.validateInput(this);
                saveToStorage();
            });
            
            input.addEventListener('paste', function(e) {
                setTimeout(() => {
                    Validator.validateInput(this);
                }, 10);
            });
        });
        
        const randomBtn = document.getElementById('random-fill-btn');
        if (randomBtn) {
            randomBtn.addEventListener('click', function() {
                console.log('Случайное заполнение - ТОЛЬКО положительные значения [0, 1]');
                
                for (let i = 1; i <= 8; i++) {
                    const input = document.querySelector(`input[name="u${i}"]`);
                    if (input) {
                        input.value = Utils.getRandomNumber(0.1, 0.9);
                    }
                }
                
                for (let i = 1; i <= 8; i++) {
                    const initialInput = document.querySelector(`input[name="u${i}"]`);
                    const limitInput = document.querySelector(`input[name="u_restrictions${i}"]`);
                    
                    if (initialInput && limitInput) {
                        const initialValue = Utils.parseNumber(initialInput.value);
                        if (!isNaN(initialValue)) {
                            const minLimit = Math.min(initialValue + 0.05, 0.99);
                            const maxLimit = 1.0;
                            limitInput.value = Utils.getRandomNumber(minLimit, maxLimit);
                        }
                    }
                }
                
                for (let i = 1; i <= 5; i++) {
                    const aInput = document.querySelector(`input[name="fak${i}_a"]`);
                    const bInput = document.querySelector(`input[name="fak${i}_b"]`);
                    
                    if (aInput) {
                       
                        aInput.value = Utils.getRandomNumber(0.1, 0.8);
                    }
                    if (bInput) {
                        bInput.value = Utils.getRandomNumber(0.1, 0.3);
                    }
                }
                
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
                
                Validator.validateAll();
                
                saveToStorage();
                
                if (statusInput) {
                    statusInput.value = 'Заполнено случайными значениями';
                    statusInput.style.color = '#2196F3';
                }
            });
        }
        
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', function() {
                console.log('Очистка формы');
                
                const inputs = document.querySelectorAll('input[type="text"]:not(#status-input)');
                inputs.forEach(input => {
                    if (input.name.startsWith('u')) {
                        input.value = '0.50';
                    } else if (input.name.startsWith('u_restrictions')) {
                        input.value = '0.80';
                    } else if (input.name.startsWith('fak') && input.name.endsWith('_a')) {
                        input.value = '0.50';
                    } else if (input.name.startsWith('fak') && input.name.endsWith('_b')) {
                        input.value = '0.10'; 
                    } else if (input.name.startsWith('f') && input.name.endsWith('_k')) {
                        input.value = '0.50';
                    } else if (input.name.startsWith('f') && input.name.endsWith('_b')) {
                        input.value = '0.50';
                    }
                    
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
        
        const calculateBtn = document.getElementById('calculate-btn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', function(e) {
                if (!Validator.validateAll()) {
                    e.preventDefault();
                    
                    const invalidInputs = document.querySelectorAll('.invalid, .invalid-limit');
                    let errorMessage = 'Пожалуйста, исправьте ошибки:\n\n';
                    
                    invalidInputs.forEach((input, index) => {
                        if (index < 5) {
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
                
                if (statusInput) {
                    statusInput.value = 'Вычисление...';
                    statusInput.style.color = '#ff9800';
                }

                saveToStorage();
                
                console.log('Форма отправляется...');
            });
        }
        
        loadFromStorage();
        
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.addEventListener('click', function() {
                saveToStorage();
            });
        });
        
        console.log('Интерфейс инициализирован');
    }
    
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
    
    initInterface();
    
    window.addEventListener('pageshow', function(event) {
        const statusInput = document.getElementById('status-input');
        if (statusInput && statusInput.value === 'Вычисление...') {
            statusInput.value = 'Готов к расчетам';
            statusInput.style.color = '';
        }
    });
    
    console.log('Модель АТС полностью инициализирована');
});