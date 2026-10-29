/* ========================================================================
   NAVIGATION MODULE
   Premium Enterprise Design System
   WCAG 2.2 AA Compliant
   ======================================================================== */

/**
 * Navigation Module
 * Handles desktop and mobile navigation
 */
(function() {
    'use strict';

    // Desktop Navigation
    const DesktopNav = {
        dropdowns: [],
        
        init: function() {
            this.dropdowns = document.querySelectorAll('[data-uk-navbar-dropdown-trigger]');
            this.bindEvents();
        },
        
        bindEvents: function() {
            this.dropdowns.forEach(function(trigger) {
                trigger.addEventListener('click', function(e) {
                    e.preventDefault();
                    DesktopNav.toggleDropdown(this);
                });
                
                // Keyboard support
                trigger.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        DesktopNav.toggleDropdown(this);
                    }
                });
            });
            
            // Close on click outside
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.uk-navbar-dropdown')) {
                    DesktopNav.closeAll();
                }
            });
            
            // Close on escape
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    DesktopNav.closeAll();
                }
            });
        },
        
        toggleDropdown: function(trigger) {
            const dropdown = trigger.nextElementSibling;
            if (!dropdown) return;
            
            const isOpen = dropdown.classList.contains('is-active');
            this.closeAll();
            
            if (!isOpen) {
                dropdown.classList.add('is-active');
                trigger.setAttribute('aria-expanded', 'true');
                
                // Focus first link
                const firstLink = dropdown.querySelector('a');
                if (firstLink) firstLink.focus();
            }
        },
        
        closeAll: function() {
            this.dropdowns.forEach(function(trigger) {
                const dropdown = trigger.nextElementSibling;
                if (dropdown) {
                    dropdown.classList.remove('is-active');
                }
                trigger.setAttribute('aria-expanded', 'false');
            });
        }
    };

    // Mobile Navigation
    const MobileNav = {
        toggle: null,
        panel: null,
        overlay: null,
        closeBtn: null,
        isOpen: false,
        lastFocused: null,
        
        init: function() {
            this.toggle = document.getElementById('mobileNavToggle');
            this.panel = document.getElementById('mobileNavPanel');
            this.overlay = document.getElementById('mobileNavOverlay');
            this.closeBtn = document.getElementById('mobileNavClose');
            
            if (!this.toggle || !this.panel) return;
            
            this.bindEvents();
        },
        
        bindEvents: function() {
            const self = this;
            
            // Toggle button
            if (this.toggle) {
                this.toggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.toggleNav();
                });
                
                // Keyboard
                this.toggle.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        self.toggleNav();
                    }
                });
            }
            
            // Close button
            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.closeNav();
                });
            }
            
            // Overlay click
            if (this.overlay) {
                this.overlay.addEventListener('click', function() {
                    self.closeNav();
                });
            }
            
            // Escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && self.isOpen) {
                    self.closeNav();
                }
            });
            
            // Dropdown triggers
            document.querySelectorAll('.mobile-nav-dropdown-trigger').forEach(function(trigger) {
                trigger.addEventListener('click', function(e) {
                    e.preventDefault();
                    const expanded = this.getAttribute('aria-expanded') === 'true';
                    this.setAttribute('aria-expanded', !expanded);
                    const dropdown = this.nextElementSibling;
                    if (dropdown) dropdown.classList.toggle('is-active');
                });
            });
            
            // Focus trap
            if (this.panel) {
                this.panel.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab') {
                        self.trapFocus(e);
                    }
                });
            }
        },
        
        toggleNav: function() {
            if (this.isOpen) {
                this.closeNav();
            } else {
                this.openNav();
            }
        },
        
        openNav: function() {
            this.isOpen = true;
            this.lastFocused = document.activeElement;
            
            this.panel.classList.add('is-active');
            if (this.overlay) this.overlay.classList.add('is-active');
            this.panel.setAttribute('aria-hidden', 'false');
            this.toggle.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';
            
            if (this.closeBtn) this.closeBtn.focus();
            
            // Announce to screen readers
            this.announce('Navigation menu opened');
        },
        
        closeNav: function() {
            this.isOpen = false;
            
            this.panel.classList.remove('is-active');
            if (this.overlay) this.overlay.classList.remove('is-active');
            this.panel.setAttribute('aria-hidden', 'true');
            this.toggle.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
            
            if (this.lastFocused) this.lastFocused.focus();
            
            // Close all dropdowns
            document.querySelectorAll('.mobile-nav-dropdown-trigger').forEach(function(trigger) {
                trigger.setAttribute('aria-expanded', 'false');
                const dropdown = trigger.nextElementSibling;
                if (dropdown) dropdown.classList.remove('is-active');
            });
            
            // Announce to screen readers
            this.announce('Navigation menu closed');
        },
        
        trapFocus: function(e) {
            const focusable = this.panel.querySelectorAll(
                'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])'
            );
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        },
        
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
        DesktopNav.init();
        MobileNav.init();
    });

})();
