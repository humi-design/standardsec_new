/* ========================================================================
   UTILITIES MODULE
   Premium Enterprise Design System
   ======================================================================== */

/**
 * Utility Functions
 */
const Utils = {
    /**
     * Debounce function
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = function() {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Throttle function
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(function() { inThrottle = false; }, limit);
            }
        };
    },
    
    /**
     * Format number with commas
     */
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },
    
    /**
     * Format currency
     */
    formatCurrency: function(amount, currency = 'INR') {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    /**
     * Format date
     */
    formatDate: function(date, format = 'short') {
        const d = new Date(date);
        const options = {
            short: { day: 'numeric', month: 'short', year: 'numeric' },
            long: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' },
            full: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric' }
        };
        return d.toLocaleDateString('en-IN', options[format] || options.short);
    },
    
    /**
     * Generate unique ID
     */
    generateId: function(prefix = 'id') {
        return prefix + '-' + Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * Copy to clipboard
     */
    copyToClipboard: function(text, callback) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                if (callback) callback(true);
            }).catch(function() {
                if (callback) callback(false);
            });
        } else {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                if (callback) callback(true);
            } catch {
                if (callback) callback(false);
            }
            document.body.removeChild(textarea);
        }
    },
    
    /**
     * Smooth scroll to element
     */
    scrollTo: function(element, offset = 0) {
        const target = typeof element === 'string' ? document.querySelector(element) : element;
        if (!target) return;
        
        const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({
            top: top,
            behavior: 'smooth'
        });
    },
    
    /**
     * Check if element is in viewport
     */
    isInViewport: function(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },
    
    /**
     * Lazy load images
     */
    lazyLoadImages: function() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                });
            });
            
            images.forEach(function(img) {
                observer.observe(img);
            });
        } else {
            // Fallback
            images.forEach(function(img) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    },
    
    /**
     * Get query parameters
     */
    getQueryParams: function() {
        const params = {};
        const searchParams = new URLSearchParams(window.location.search);
        for (const [key, value] of searchParams) {
            params[key] = value;
        }
        return params;
    },
    
    /**
     * Set query parameters
     */
    setQueryParams: function(params) {
        const url = new URL(window.location);
        Object.keys(params).forEach(function(key) {
            url.searchParams.set(key, params[key]);
        });
        window.history.pushState({}, '', url);
    },
    
    /**
     * Check if touch device
     */
    isTouchDevice: function() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },
    
    /**
     * Check if reduced motion preferred
     */
    prefersReducedMotion: function() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },
    
    /**
     * Announce to screen readers
     */
    announce: function(message, priority = 'polite') {
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', priority);
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        announcer.textContent = message;
        document.body.appendChild(announcer);
        setTimeout(function() {
            announcer.remove();
        }, 1000);
    }
};

/**
 * Scroll Animations Module
 */
const ScrollAnimations = {
    init: function() {
        this.setupIntersectionObserver();
        this.setupScrollProgress();
    },
    
    setupIntersectionObserver: function() {
        const elements = document.querySelectorAll('.scroll-animate, [data-animate], .stagger-children');
        if (elements.length === 0) return;
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        elements.forEach(function(el) {
            observer.observe(el);
        });
    },
    
    setupScrollProgress: function() {
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        document.body.appendChild(progressBar);
        
        const updateProgress = Utils.throttle(function() {
            const scrollTop = window.pageYOffset;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = (scrollTop / docHeight) * 100;
            progressBar.style.width = progress + '%';
        }, 100);
        
        window.addEventListener('scroll', updateProgress);
    }
};

/**
 * Initialize on DOM ready
 */
document.addEventListener('DOMContentLoaded', function() {
    ScrollAnimations.init();
    Utils.lazyLoadImages();
});
