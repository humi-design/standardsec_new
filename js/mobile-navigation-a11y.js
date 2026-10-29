/* ========================================================================
   MOBILE NAVIGATION ACCESSIBILITY MODULE
   Standard Securities & Investment Intermediates Ltd.
   WCAG 2.2 AA Compliant | Keyboard Optimized
   
   Features:
   - Keyboard navigation (Tab, Shift+Tab, Escape)
   - Focus trapping within modal
   - Screen reader announcements
   - Proper ARIA attributes
   - Escape key closes menu
   - Click outside closes menu
   ======================================================================== */

(function() {
    'use strict';

    const MobileNavA11y = {
        modal: null,
        toggle: null,
        closeBtn: null,
        focusableElements: [],
        previouslyFocused: null,
        isOpen: false,

        init: function() {
            this.modal = document.getElementById('mobile-nav-modal');
            this.toggle = document.querySelector('.mobile-nav-toggle, [href="#mobile-nav-modal"]');
            this.closeBtn = this.modal ? this.modal.querySelector('.uk-modal-close-full, .uk-close-large') : null;

            if (!this.modal || !this.toggle) {
                console.log('Mobile navigation elements not found - skipping initialization');
                return;
            }

            this.setupEventListeners();
            this.setupAccessibility();
            this.prepareFocusableElements();
        },

        setupEventListeners: function() {
            const self = this;

            // Toggle button click
            this.toggle.addEventListener('click', function(e) {
                e.preventDefault();
                self.toggleModal();
            });

            // Toggle button keyboard
            this.toggle.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    self.toggleModal();
                }
            });

            // Close button
            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.closeModal();
                });

                this.closeBtn.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        self.closeModal();
                    }
                });
            }

            // Escape key closes modal
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && self.isOpen) {
                    self.closeModal();
                    if (self.toggle) {
                        self.toggle.focus();
                    }
                }
            });

            // Click outside closes modal
            this.modal.addEventListener('click', function(e) {
                if (e.target === self.modal) {
                    self.closeModal();
                }
            });

            // Focus trap
            this.modal.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    self.trapFocus(e);
                }
            });

            // Handle dropdown toggles within mobile nav
            const dropdownTriggers = this.modal.querySelectorAll('.uk-parent > a');
            dropdownTriggers.forEach(function(trigger) {
                trigger.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.toggleDropdown(this);
                });

                trigger.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        self.toggleDropdown(this);
                    } else if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        const dropdown = trigger.nextElementSibling;
                        if (dropdown) {
                            const firstLink = dropdown.querySelector('a');
                            if (firstLink) firstLink.focus();
                        }
                    }
                });
            });
        },

        setupAccessibility: function() {
            // Toggle button
            if (this.toggle) {
                this.toggle.setAttribute('aria-expanded', 'false');
                this.toggle.setAttribute('aria-controls', 'mobile-nav-modal');
                if (!this.toggle.getAttribute('aria-label')) {
                    this.toggle.setAttribute('aria-label', 'Open navigation menu');
                }
            }

            // Modal
            this.modal.setAttribute('role', 'dialog');
            this.modal.setAttribute('aria-modal', 'true');
            this.modal.setAttribute('aria-hidden', 'true');
            if (!this.modal.getAttribute('aria-labelledby')) {
                const title = this.modal.querySelector('h1, h2, h3');
                if (title && !title.id) {
                    title.id = 'mobile-nav-title';
                }
                if (title && title.id) {
                    this.modal.setAttribute('aria-labelledby', title.id);
                }
            }

            // Close button
            if (this.closeBtn && !this.closeBtn.getAttribute('aria-label')) {
                this.closeBtn.setAttribute('aria-label', 'Close navigation menu');
            }
        },

        prepareFocusableElements: function() {
            if (!this.modal) return;
            
            const selector = [
                'a[href]',
                'button:not([disabled])',
                'input:not([disabled])',
                'select:not([disabled])',
                'textarea:not([disabled])',
                '[tabindex]:not([tabindex="-1"])'
            ].join(',');

            this.focusableElements = Array.from(this.modal.querySelectorAll(selector));
        },

        toggleModal: function() {
            if (this.isOpen) {
                this.closeModal();
            } else {
                this.openModal();
            }
        },

        openModal: function() {
            if (!this.modal) return;

            this.isOpen = true;
            this.previouslyFocused = document.activeElement;

            // Show modal
            this.modal.classList.add('uk-open');
            this.modal.setAttribute('aria-hidden', 'false');

            // Update toggle
            if (this.toggle) {
                this.toggle.setAttribute('aria-expanded', 'true');
            }

            // Focus management
            this.prepareFocusableElements();
            if (this.closeBtn) {
                this.closeBtn.focus();
            } else if (this.focusableElements.length > 0) {
                this.focusableElements[0].focus();
            }

            // Announce to screen readers
            this.announce('Navigation menu opened');

            // Prevent body scroll
            document.body.style.overflow = 'hidden';
        },

        closeModal: function() {
            if (!this.modal) return;

            this.isOpen = false;

            // Hide modal
            this.modal.classList.remove('uk-open');
            this.modal.setAttribute('aria-hidden', 'true');

            // Update toggle
            if (this.toggle) {
                this.toggle.setAttribute('aria-expanded', 'false');
            }

            // Restore focus
            if (this.previouslyFocused) {
                this.previouslyFocused.focus();
            }

            // Announce to screen readers
            this.announce('Navigation menu closed');

            // Restore body scroll
            document.body.style.overflow = '';
        },

        trapFocus: function(e) {
            if (this.focusableElements.length === 0) return;

            const firstFocusable = this.focusableElements[0];
            const lastFocusable = this.focusableElements[this.focusableElements.length - 1];

            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        },

        toggleDropdown: function(trigger) {
            const parent = trigger.parentElement;
            const dropdown = parent.querySelector('ul');
            
            if (!dropdown) return;

            const isExpanded = trigger.getAttribute('aria-expanded') === 'true';

            // Close all other dropdowns
            const allTriggers = this.modal.querySelectorAll('.uk-parent > a');
            allTriggers.forEach(function(t) {
                if (t !== trigger) {
                    t.setAttribute('aria-expanded', 'false');
                    const d = t.parentElement.querySelector('ul');
                    if (d) d.style.display = 'none';
                }
            });

            // Toggle current
            trigger.setAttribute('aria-expanded', !isExpanded);
            dropdown.style.display = isExpanded ? 'none' : 'block';
        },

        announce: function(message) {
            const announcer = document.createElement('div');
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.className = 'sr-only';
            announcer.textContent = message;
            document.body.appendChild(announcer);

            // Remove after announcement
            setTimeout(function() {
                if (announcer.parentNode) {
                    announcer.parentNode.removeChild(announcer);
                }
            }, 1000);
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            MobileNavA11y.init();
        });
    } else {
        MobileNavA11y.init();
    }

    // Expose for external access
    window.MobileNavA11y = MobileNavA11y;

})();
