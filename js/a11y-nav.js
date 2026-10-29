/* ========================================================================
   MOBILE NAVIGATION ACCESSIBILITY (WCAG 2.2 - 4.1.2 Name, Role, Value)
   The hamburger button opens the UIkit modal via data-uk-toggle; this module
   keeps aria-expanded / aria-controls in sync with the modal's open state so
   assistive technology is told whether the menu is open or closed.
   ======================================================================== */
(function () {
    'use strict';

    function init() {
        var toggle = document.querySelector('.in-mobile-nav button[data-uk-toggle]');
        var modal = document.getElementById('mobile-nav-modal');

        if (toggle && modal) {
            if (!toggle.getAttribute('aria-controls')) {
                toggle.setAttribute('aria-controls', 'mobile-nav-modal');
            }
            if (!toggle.getAttribute('aria-expanded')) {
                toggle.setAttribute('aria-expanded', 'false');
            }

            var sync = function () {
                var open = modal.classList.contains('uk-open');
                toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
                toggle.setAttribute('aria-label', open ? 'Close mobile navigation menu' : 'Open mobile navigation menu');
            };

            // UIkit emits these events on the modal element.
            ['show', 'shown', 'hide', 'hidden'].forEach(function (name) {
                modal.addEventListener(name, sync);
            });

            // Fallback for browsers where UIkit has not initialised yet.
            toggle.addEventListener('click', function () {
                setTimeout(sync, 50);
            });

            // Escape returns focus to the toggle once the modal has closed.
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && modal.classList.contains('uk-open')) {
                    setTimeout(function () { toggle.focus(); }, 50);
                }
            });

            sync();
        }

        // Embeds must carry an accessible name (4.1.2). Google Translate and
        // the reCAPTCHA helper inject their own frames; only author iframes
        // without a title are labelled here.
        document.querySelectorAll('iframe:not([title])').forEach(function (frame) {
            var src = frame.getAttribute('src') || '';
            if (!src) return;
            var title = 'Embedded content';
            if (src.indexOf('google.com/maps') !== -1) {
                title = 'Map showing our office location';
            } else if (src.indexOf('botframework.com') !== -1) {
                title = 'Chatbot conversation window';
            } else if (src.indexOf('recaptcha') !== -1) {
                title = 'reCAPTCHA verification';
            }
            frame.setAttribute('title', title);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
