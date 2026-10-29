/* ========================================================================
   ACCESSIBILITY MODULE
   Premium Enterprise Design System
   WCAG 2.2 AA Compliant
   ======================================================================== */

/**
 * Accessibility Module
 * Handles accessibility features and preferences
 */
(function() {
    'use strict';

    const Accessibility = {
        widget: null,
        panel: null,
        toggle: null,
        isOpen: false,
        
        init: function() {
            this.toggle = document.getElementById('accessibilityToggle');
            this.panel = document.getElementById('accessibilityPanel');
            
            if (!this.toggle || !this.panel) return;
            
            this.bindEvents();
            this.loadPreferences();
        },
        
        bindEvents: function() {
            const self = this;
            
            // Toggle button
            this.toggle.addEventListener('click', function(e) {
                e.preventDefault();
                self.togglePanel();
            });
            
            // Keyboard
            this.toggle.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    self.togglePanel();
                }
            });
            
            // Close on escape
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && self.isOpen) {
                    self.closePanel();
                }
            });
            
            // Close on click outside
            document.addEventListener('click', function(e) {
                if (!self.panel.contains(e.target) && !self.toggle.contains(e.target)) {
                    self.closePanel();
                }
            });
        },
        
        togglePanel: function() {
            if (this.isOpen) {
                this.closePanel();
            } else {
                this.openPanel();
            }
        },
        
        openPanel: function() {
            this.isOpen = true;
            this.panel.classList.remove('is-hidden');
            this.panel.setAttribute('aria-hidden', 'false');
            this.toggle.setAttribute('aria-expanded', 'true');
            
            // Focus first button in panel
            const firstBtn = this.panel.querySelector('button, a');
            if (firstBtn) firstBtn.focus();
        },
        
        closePanel: function() {
            this.isOpen = false;
            this.panel.classList.add('is-hidden');
            this.panel.setAttribute('aria-hidden', 'true');
            this.toggle.setAttribute('aria-expanded', 'false');
            this.toggle.focus();
        },
        
        loadPreferences: function() {
            // Font size
            const savedFontSize = localStorage.getItem('fontSize');
            if (savedFontSize) {
                document.documentElement.style.fontSize = savedFontSize + 'px';
            }
            
            // Dark mode
            const savedDarkMode = localStorage.getItem('darkMode');
            if (savedDarkMode === 'true') {
                document.body.classList.add('dark-mode');
            }
        }
    };

    /**
     * Font Size Control
     */
    window.changeFontSize = function(delta) {
        const html = document.documentElement;
        const current = parseFloat(window.getComputedStyle(html).fontSize) || 16;
        const newSize = Math.max(12, Math.min(24, current + (delta * 2)));
        html.style.fontSize = newSize + 'px';
        localStorage.setItem('fontSize', newSize);
        
        // Announce change
        AccessibilityModule.announce('Font size changed to ' + newSize + ' pixels');
    };

    /**
     * Reset Font Size
     */
    window.resetFontSize = function() {
        document.documentElement.style.fontSize = '16px';
        localStorage.setItem('fontSize', '16');
        AccessibilityModule.announce('Font size reset to default');
    };

    /**
     * Dark Mode Toggle
     */
    window.toggleDarkMode = function() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        
        const message = isDark ? 'Dark mode enabled' : 'Dark mode disabled';
        AccessibilityModule.announce(message);
    };

    /**
     * High Contrast Toggle
     */
    window.toggleHighContrast = function() {
        document.body.classList.toggle('high-contrast');
        const isHighContrast = document.body.classList.contains('high-contrast');
        localStorage.setItem('highContrast', isHighContrast);
        
        const message = isHighContrast ? 'High contrast mode enabled' : 'High contrast mode disabled';
        AccessibilityModule.announce(message);
    };

    /**
     * Underline Links Toggle
     */
    window.toggleLinkUnderline = function() {
        document.body.classList.toggle('links-underlined');
        const isUnderlined = document.body.classList.contains('links-underlined');
        localStorage.setItem('linkUnderline', isUnderlined);
        
        const message = isUnderlined ? 'Links are now underlined' : 'Link underlines removed';
        AccessibilityModule.announce(message);
    };

    /**
     * Read Content Aloud
     */
    window.readContent = function() {
        const content = document.querySelector('main') || document.body;
        const text = content.innerText;
        
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-IN';
            utterance.rate = 1;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
            AccessibilityModule.announce('Reading page content');
        }
    };

    /**
     * Stop Reading
     */
    window.stopReading = function() {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
            AccessibilityModule.announce('Reading stopped');
        }
    };

    /**
     * Accessibility Module (Internal)
     */
    const AccessibilityModule = {
        announce: function(message) {
            const announcer = document.createElement('div');
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.className = 'sr-only';
            announcer.textContent = message;
            document.body.appendChild(announcer);
            setTimeout(function() {
                announcer.remove();
            }, 1000);
        }
    };

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        Accessibility.init();
        initMobileNavAccessibility();
        initCarouselAccessibility();
        initFormAccessibility();
    });

})();

/* ========================================================================
   MOBILE NAVIGATION ACCESSIBILITY
   Focus trapping and keyboard support
   ======================================================================== */
function initMobileNavAccessibility() {
    // Find mobile nav toggles
    var navToggles = document.querySelectorAll('[class*="hamburger"], [class*="uk-navbar-toggle"], button[class*="toggle"], a[href*="menu"]');
    
    navToggles.forEach(function(toggle) {
        // Add aria attributes
        if (!toggle.getAttribute('aria-expanded')) {
            toggle.setAttribute('aria-expanded', 'false');
        }
        if (!toggle.getAttribute('aria-label')) {
            toggle.setAttribute('aria-label', 'Toggle navigation menu');
        }
    });
    
    // Escape key closes menus
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            var openMenus = document.querySelectorAll('[aria-expanded="true"]');
            openMenus.forEach(function(menu) {
                menu.setAttribute('aria-expanded', 'false');
            });
        }
    });
}

/* ========================================================================
   CAROUSEL/SLIDESHOW ACCESSIBILITY
   Pause control for auto-advancing content
   ======================================================================== */
function initCarouselAccessibility() {
    // Find UIkit slideshows
    if (typeof UIkit !== 'undefined') {
        var slideshows = document.querySelectorAll('[data-uk-slideshow]');
        
        slideshows.forEach(function(slideshow) {
            var nav = slideshow.querySelector('.uk-slideshow-nav');
            if (!nav) return;
            
            // Find or create pause button
            var pauseBtn = nav.querySelector('[aria-label*="Pause"], [aria-label*="Play"]');
            if (!pauseBtn) {
                pauseBtn = document.createElement('button');
                pauseBtn.setAttribute('aria-label', 'Pause slideshow');
                pauseBtn.textContent = 'Pause';
                nav.appendChild(pauseBtn);
            }
            
            var isPaused = false;
            
            pauseBtn.addEventListener('click', function() {
                isPaused = !isPaused;
                var ukSlideshow = UIkit.slideshow(slideshow);
                
                if (isPaused) {
                    ukSlideshow.pause();
                    this.setAttribute('aria-label', 'Play slideshow');
                    this.textContent = 'Play';
                } else {
                    ukSlideshow.start();
                    this.setAttribute('aria-label', 'Pause slideshow');
                    this.textContent = 'Pause';
                }
            });
        });
    }
}

/* ========================================================================
   FORM ACCESSIBILITY
   Validation and error announcements
   ======================================================================== */
function initFormAccessibility() {
    var forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        var inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(function(input) {
            // Ensure required fields have aria-required
            if (input.hasAttribute('required') && !input.hasAttribute('aria-required')) {
                input.setAttribute('aria-required', 'true');
            }
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            var invalidInputs = form.querySelectorAll(':invalid');
            var firstInvalid = null;
            
            invalidInputs.forEach(function(input) {
                input.setAttribute('aria-invalid', 'true');
                if (!firstInvalid) firstInvalid = input;
                
                // Find or create error message
                var errorId = input.id + '-error';
                var errorMsg = document.getElementById(errorId);
                
                if (!errorMsg) {
                    errorMsg = document.createElement('div');
                    errorMsg.id = errorId;
                    errorMsg.className = 'form-error';
                    errorMsg.setAttribute('role', 'alert');
                    errorMsg.setAttribute('aria-live', 'polite');
                    input.parentNode.insertBefore(errorMsg, input.nextSibling);
                }
                
                errorMsg.textContent = input.validationMessage || 'This field is required';
            });
            
            // Clear valid fields
            var validInputs = form.querySelectorAll('input:valid, textarea:valid');
            validInputs.forEach(function(input) {
                input.setAttribute('aria-invalid', 'false');
                var errorId = input.id + '-error';
                var errorMsg = document.getElementById(errorId);
                if (errorMsg) errorMsg.remove();
            });
            
            // Focus first invalid and announce
            if (firstInvalid) {
                e.preventDefault();
                firstInvalid.focus();
                announceToScreenReader('Form has errors. Please correct the highlighted fields.');
            }
        });
        
        // Real-time validation on blur
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.setAttribute('aria-invalid', 'false');
                } else if (this.value) {
                    this.setAttribute('aria-invalid', 'true');
                }
            });
        });
    });
}

/* ========================================================================
   SCREEN READER ANNOUNCEMENTS
   ======================================================================== */
function announceToScreenReader(message) {
    var announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    announcer.textContent = message;
    document.body.appendChild(announcer);
    setTimeout(function() {
        announcer.remove();
    }, 1000);
}
