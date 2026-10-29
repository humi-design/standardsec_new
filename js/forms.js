/* ========================================================================
   FORMS MODULE
   Premium Enterprise Design System
   WCAG 2.2 AA Compliant
   ======================================================================== */

/**
 * Forms Module
 * Handles form validation and interactions
 */
(function() {
    'use strict';

    const Forms = {
        init: function() {
            this.initValidation();
            this.initAutoComplete();
            this.initCharacterCounters();
            this.initPasswordToggle();
            this.initFormHints();
        },
        
        /**
         * Initialize Form Validation
         */
        initValidation: function() {
            const forms = document.querySelectorAll('form[data-validate], form[data-ajax]');
            
            forms.forEach(function(form) {
                form.setAttribute('novalidate', 'true');
                
                form.addEventListener('submit', function(e) {
                    if (!Forms.validateForm(form)) {
                        e.preventDefault();
                        Forms.focusFirstError(form);
                    }
                });
            });
            
            // Real-time validation
            const inputs = document.querySelectorAll(
                'input[required], textarea[required], select[required], ' +
                'input[data-validate], textarea[data-validate], select[data-validate]'
            );
            
            inputs.forEach(function(input) {
                input.addEventListener('blur', function() {
                    Forms.validateInput(this);
                });
                
                input.addEventListener('input', function() {
                    if (this.classList.contains('error')) {
                        Forms.validateInput(this);
                    }
                });
                
                // Remove error on focus
                input.addEventListener('focus', function() {
                    Forms.clearError(this);
                });
            });
        },
        
        /**
         * Validate entire form
         */
        validateForm: function(form) {
            let isValid = true;
            let firstError = null;
            
            const inputs = form.querySelectorAll(
                'input[required], textarea[required], select[required], ' +
                'input[data-validate], textarea[data-validate], select[data-validate]'
            );
            
            inputs.forEach(function(input) {
                if (!Forms.validateInput(input)) {
                    isValid = false;
                    if (!firstError) {
                        firstError = input;
                    }
                }
            });
            
            // Custom form validation
            if (form.dataset.validate) {
                const customValid = Forms.customValidation(form);
                if (!customValid) {
                    isValid = false;
                }
            }
            
            return isValid;
        },
        
        /**
         * Validate single input
         */
        validateInput: function(input) {
            Forms.clearError(input);
            
            // Required check
            if (input.hasAttribute('required') && !input.value.trim()) {
                Forms.showError(input, 'This field is required');
                return false;
            }
            
            // Type-specific validation
            switch (input.type) {
                case 'email':
                    if (input.value && !Forms.isValidEmail(input.value)) {
                        Forms.showError(input, 'Please enter a valid email address');
                        return false;
                    }
                    break;
                    
                case 'tel':
                    if (input.value && !Forms.isValidPhone(input.value)) {
                        Forms.showError(input, 'Please enter a valid phone number');
                        return false;
                    }
                    break;
                    
                case 'url':
                    if (input.value && !Forms.isValidUrl(input.value)) {
                        Forms.showError(input, 'Please enter a valid URL');
                        return false;
                    }
                    break;
                    
                case 'password':
                    if (input.value && input.dataset.minLength) {
                        if (input.value.length < parseInt(input.dataset.minLength)) {
                            Forms.showError(input, 'Password must be at least ' + input.dataset.minLength + ' characters');
                            return false;
                        }
                    }
                    break;
            }
            
            // Custom validation patterns
            if (input.dataset.pattern) {
                const regex = new RegExp(input.dataset.pattern);
                if (input.value && !regex.test(input.value)) {
                    Forms.showError(input, input.dataset.patternMessage || 'Invalid format');
                    return false;
                }
            }
            
            // Min/max length
            if (input.dataset.minLength && input.value.length < parseInt(input.dataset.minLength)) {
                Forms.showError(input, 'Minimum ' + input.dataset.minLength + ' characters required');
                return false;
            }
            
            if (input.dataset.maxLength && input.value.length > parseInt(input.dataset.maxLength)) {
                Forms.showError(input, 'Maximum ' + input.dataset.maxLength + ' characters allowed');
                return false;
            }
            
            return true;
        },
        
        /**
         * Custom form validation
         */
        customValidation: function(form) {
            // Password confirmation
            const password = form.querySelector('input[type="password"][data-confirm]');
            if (password) {
                const confirm = form.querySelector('input[data-confirm-target]');
                if (confirm && password.value !== confirm.value) {
                    Forms.showError(confirm, 'Passwords do not match');
                    return false;
                }
            }
            
            // Checkbox agreement
            const agreement = form.querySelector('input[type="checkbox"][required]');
            if (agreement && !agreement.checked) {
                Forms.showError(agreement, 'You must agree to continue');
                return false;
            }
            
            return true;
        },
        
        /**
         * Show error message
         */
        showError: function(input, message) {
            input.classList.add('error');
            input.setAttribute('aria-invalid', 'true');
            input.setAttribute('aria-describedby', 'error-' + input.id);
            
            const errorId = 'error-' + (input.id || Math.random().toString(36).substr(2, 9));
            
            let errorEl = input.parentElement.querySelector('.form-error:not(.hidden)');
            if (!errorEl) {
                errorEl = document.createElement('span');
                errorEl.id = errorId;
                errorEl.className = 'form-error';
                errorEl.setAttribute('role', 'alert');
                input.parentElement.appendChild(errorEl);
            }
            
            errorEl.textContent = message;
            input.setAttribute('aria-describedby', errorId);
        },
        
        /**
         * Clear error message
         */
        clearError: function(input) {
            input.classList.remove('error');
            input.removeAttribute('aria-invalid');
            
            const errorEl = input.parentElement.querySelector('.form-error');
            if (errorEl) {
                errorEl.remove();
            }
        },
        
        /**
         * Focus first error field
         */
        focusFirstError: function(form) {
            const firstError = form.querySelector('.error');
            if (firstError) {
                firstError.focus();
                
                // Scroll into view
                firstError.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        },
        
        /**
         * Validation helpers
         */
        isValidEmail: function(value) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        },
        
        isValidPhone: function(value) {
            return /^[\d\s\-+()]{10,}$/.test(value);
        },
        
        isValidUrl: function(value) {
            try {
                new URL(value);
                return true;
            } catch {
                return false;
            }
        },
        
        /**
         * Initialize auto-complete suggestions
         */
        initAutoComplete: function() {
            const inputs = document.querySelectorAll('input[data-autocomplete]');
            
            inputs.forEach(function(input) {
                const suggestions = input.dataset.autocomplete.split(',');
                const datalist = document.createElement('datalist');
                datalist.id = 'autocomplete-' + input.id;
                
                suggestions.forEach(function(suggestion) {
                    const option = document.createElement('option');
                    option.value = suggestion.trim();
                    datalist.appendChild(option);
                });
                
                input.setAttribute('list', datalist.id);
                input.parentElement.appendChild(datalist);
            });
        },
        
        /**
         * Initialize character counters
         */
        initCharacterCounters: function() {
            const textareas = document.querySelectorAll('textarea[data-max-length]');
            
            textareas.forEach(function(textarea) {
                const maxLength = parseInt(textarea.dataset.maxLength);
                const counter = document.createElement('div');
                counter.className = 'form-help character-counter';
                counter.setAttribute('aria-live', 'polite');
                
                const updateCounter = function() {
                    const remaining = maxLength - textarea.value.length;
                    counter.textContent = remaining + ' characters remaining';
                    counter.classList.toggle('text-danger', remaining < 20);
                };
                
                textarea.addEventListener('input', updateCounter);
                textarea.parentElement.appendChild(counter);
                updateCounter();
            });
        },
        
        /**
         * Initialize password visibility toggle
         */
        initPasswordToggle: function() {
            const toggles = document.querySelectorAll('input[type="password"]');
            
            toggles.forEach(function(password) {
                const wrapper = password.parentElement;
                const toggle = document.createElement('button');
                toggle.type = 'button';
                toggle.className = 'password-toggle';
                toggle.setAttribute('aria-label', 'Toggle password visibility');
                toggle.innerHTML = '<span class="sr-only">Show</span><span aria-hidden="true">👁</span>';
                
                toggle.addEventListener('click', function() {
                    if (password.type === 'password') {
                        password.type = 'text';
                        toggle.innerHTML = '<span class="sr-only">Hide</span><span aria-hidden="true">🙈</span>';
                    } else {
                        password.type = 'password';
                        toggle.innerHTML = '<span class="sr-only">Show</span><span aria-hidden="true">👁</span>';
                    }
                });
                
                wrapper.style.position = 'relative';
                wrapper.appendChild(toggle);
            });
        },
        
        /**
         * Initialize form hints
         */
        initFormHints: function() {
            const inputs = document.querySelectorAll('input[aria-describedby], textarea[aria-describedby]');
            
            inputs.forEach(function(input) {
                const hintId = input.getAttribute('aria-describedby');
                if (hintId) {
                    input.setAttribute('aria-describedby', hintId + ' ' + hintId + '-hint');
                }
            });
        }
    };

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        Forms.init();
    });

})();
