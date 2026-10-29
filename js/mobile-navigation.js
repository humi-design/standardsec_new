/* ========================================================================
   MOBILE NAVIGATION MODULE
   Standard Securities & Investment Intermediates Ltd.
   WCAG 2.2 AA Compliant | Touch-Optimized
   
   Features:
   - Smooth animations
   - Keyboard accessible
   - Screen reader friendly
   - Focus trapping
   - Close on outside click
   - Close on Escape
   - Correct ARIA attributes
   - Touch optimized
   ======================================================================== */

(function() {
    'use strict';

    const MobileNav = {
        toggle: null,
        panel: null,
        overlay: null,
        closeBtn: null,
        dropdownTriggers: null,
        isOpen: false,
        lastFocusedElement: null,
        scrollPosition: 0,

        init: function() {
            this.toggle = document.getElementById('mobileNavToggle');
            this.panel = document.getElementById('mobileNavPanel');
            this.overlay = document.getElementById('mobileNavOverlay');
            this.closeBtn = document.getElementById('mobileNavClose');
            this.dropdownTriggers = document.querySelectorAll('.mobile-nav-dropdown-trigger');

            if (!this.toggle || !this.panel) {
                console.log('Mobile navigation elements not found');
                return;
            }

            this.bindEvents();
            this.setupAccessibility();
        },

        bindEvents: function() {
            const self = this;

            // Toggle button - click
            this.toggle.addEventListener('click', function(e) {
                e.preventDefault();
                self.toggleNav();
            });

            // Toggle button - keyboard
            this.toggle.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    self.toggleNav();
                }
            });

            // Close button - click
            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.closeNav();
                });
            }

            // Overlay - click
            if (this.overlay) {
                this.overlay.addEventListener('click', function() {
                    self.closeNav();
                });

                // Prevent scroll on overlay
                this.overlay.addEventListener('touchmove', function(e) {
                    if (self.isOpen) {
                        e.preventDefault();
                    }
                }, { passive: false });
            }

            // Escape key - close nav
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && self.isOpen) {
                    self.closeNav();
                    self.toggle.focus();
                }
            });

            // Dropdown triggers
            this.dropdownTriggers.forEach(function(trigger) {
                trigger.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.toggleDropdown(this);
                });

                trigger.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        self.toggleDropdown(this);
                    }
                });
            });

            // Panel touch handling
            if (this.panel) {
                this.panel.addEventListener('touchmove', function(e) {
                    // Allow natural scrolling within panel
                    const scrollable = this;
                    const scrollTop = scrollable.scrollTop;
                    const scrollHeight = scrollable.scrollHeight;
                    const height = scrollable.clientHeight;
                    const offset = e.touches[0].clientY;

                    if ((scrollTop === 0 && offset > 0) ||
                        (scrollTop + height >= scrollHeight && offset < 0)) {
                        e.preventDefault();
                    }
                }, { passive: false });

                // Focus trap
                this.panel.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab') {
                        self.trapFocus(e);
                    }
                });
            }

            // Prevent body scroll when nav is open
            document.body.addEventListener('touchmove', function(e) {
                if (self.isOpen) {
                    if (!self.panel || !self.panel.contains(e.target)) {
                        e.preventDefault();
                    }
                }
            }, { passive: false });

            // Handle window resize - close nav if switching to desktop
            window.addEventListener('resize', function() {
                if (window.innerWidth >= 1024 && self.isOpen) {
                    self.closeNav();
                }
            });

            // Handle orientation change
            window.addEventListener('orientationchange', function() {
                setTimeout(function() {
                    if (window.innerWidth >= 1024 && self.isOpen) {
                        self.closeNav();
                    }
                }, 100);
            });
        },

        setupAccessibility: function() {
            // Set initial ARIA states
            if (this.toggle) {
                this.toggle.setAttribute('aria-expanded', 'false');
                this.toggle.setAttribute('aria-controls', 'mobileNavPanel');
                this.toggle.setAttribute('aria-label', 'Open navigation menu');
            }

            if (this.panel) {
                this.panel.setAttribute('aria-hidden', 'true');
                this.panel.setAttribute('role', 'dialog');
                this.panel.setAttribute('aria-modal', 'true');
                this.panel.setAttribute('aria-label', 'Navigation menu');
            }

            if (this.closeBtn) {
                this.closeBtn.setAttribute('aria-label', 'Close navigation menu');
            }

            // Dropdown triggers
            this.dropdownTriggers.forEach(function(trigger) {
                const dropdown = trigger.nextElementSibling;
                if (dropdown && dropdown.classList.contains('mobile-nav-dropdown')) {
                    const dropdownId = 'dropdown-' + Math.random().toString(36).substr(2, 9);
                    trigger.setAttribute('aria-expanded', 'false');
                    trigger.setAttribute('aria-controls', dropdownId);
                    dropdown.id = dropdownId;
                }
            });
        },

        toggleNav: function() {
            if (this.isOpen) {
                this.closeNav();
            } else {
                this.openNav();
            }
        },

        openNav: function() {
            if (!this.toggle || !this.panel) return;

            this.isOpen = true;
            this.lastFocusedElement = document.activeElement;
            this.scrollPosition = window.pageYOffset;

            // Add classes
            this.panel.classList.add('is-active');
            this.toggle.classList.add('is-active');
            if (this.overlay) {
                this.overlay.classList.add('is-active');
            }

            // Update ARIA
            this.panel.setAttribute('aria-hidden', 'false');
            this.toggle.setAttribute('aria-expanded', 'true');
            this.toggle.setAttribute('aria-label', 'Close navigation menu');

            // Lock body scroll
            document.body.classList.add('nav-open');
            document.body.style.top = '-' + this.scrollPosition + 'px';

            // Focus close button
            if (this.closeBtn) {
                this.closeBtn.focus();
            }

            // Announce to screen readers
            this.announce('Navigation menu opened');

            // Close other dropdowns
            this.closeAllDropdowns();
        },

        closeNav: function() {
            if (!this.panel) return;

            this.isOpen = false;

            // Remove classes
            this.panel.classList.remove('is-active');
            this.toggle.classList.remove('is-active');
            if (this.overlay) {
                this.overlay.classList.remove('is-active');
            }

            // Update ARIA
            this.panel.setAttribute('aria-hidden', 'true');
            this.toggle.setAttribute('aria-expanded', 'false');
            this.toggle.setAttribute('aria-label', 'Open navigation menu');

            // Unlock body scroll
            document.body.classList.remove('nav-open');
            document.body.style.top = '';

            // Restore scroll position
            window.scrollTo(0, this.scrollPosition);

            // Return focus
            if (this.lastFocusedElement) {
                this.lastFocusedElement.focus();
            }

            // Announce to screen readers
            this.announce('Navigation menu closed');

            // Close all dropdowns
            this.closeAllDropdowns();
        },

        toggleDropdown: function(trigger) {
            const dropdown = trigger.nextElementSibling;
            if (!dropdown) return;

            const isExpanded = trigger.getAttribute('aria-expanded') === 'true';

            // Close other dropdowns
            this.dropdownTriggers.forEach(function(t) {
                if (t !== trigger) {
                    t.setAttribute('aria-expanded', 'false');
                    const d = t.nextElementSibling;
                    if (d) d.classList.remove('is-active');
                }
            });

            // Toggle current dropdown
            trigger.setAttribute('aria-expanded', !isExpanded);
            dropdown.classList.toggle('is-active', !isExpanded);
        },

        closeAllDropdowns: function() {
            this.dropdownTriggers.forEach(function(trigger) {
                trigger.setAttribute('aria-expanded', 'false');
                const dropdown = trigger.nextElementSibling;
                if (dropdown) dropdown.classList.remove('is-active');
            });
        },

        trapFocus: function(e) {
            const focusableElements = this.panel.querySelectorAll(
                'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );

            const firstFocusable = focusableElements[0];
            const lastFocusable = focusableElements[focusableElements.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
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
            MobileNav.init();
        });
    } else {
        MobileNav.init();
    }

    // Expose for external access
    window.MobileNav = MobileNav;

})();
