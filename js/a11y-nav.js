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

        // ---- Extreme text-enlargement fallback (1.4.4) -------------------
        // The horizontal bar fits on one row down to its 960px breakpoint at
        // normal text sizes. Under heavy text enlargement the links can grow
        // past the container again; instead of clipping them or letting them
        // wrap onto unordered rows, collapse the bar into the same accessible
        // hamburger menu used at narrow viewports. No effect at normal sizes.
        var navBar = document.querySelector('header nav.uk-navbar-container');
        var navList = navBar ? navBar.querySelector('.uk-navbar-nav') : null;
        var mobileBar = document.querySelector('.in-mobile-nav');
        if (navBar && navList && mobileBar) {
            var collapsed = false;
            var apply = function () {
                if (window.innerWidth < 960) { // base stylesheets already do this
                    navBar.style.removeProperty('display');
                    mobileBar.style.removeProperty('display');
                    collapsed = false;
                    return;
                }
                if (collapsed) navBar.style.removeProperty('display');
                var overflowing = navList.scrollWidth > navBar.clientWidth + 1;
                if (overflowing) {
                    navBar.style.display = 'none';
                    // The bar is a flex container (uk-flex uk-flex-right); keep
                    // that, but beat uikit's `.uk-hidden\@m { display:none !important }`.
                    mobileBar.style.setProperty('display', 'flex', 'important');
                } else {
                    navBar.style.removeProperty('display');
                    mobileBar.style.removeProperty('display');
                }
                collapsed = overflowing;
            };
            var pending = false;
            var schedule = function () {
                if (pending) return;
                pending = true;
                requestAnimationFrame(function () { pending = false; apply(); });
            };
            apply();
            window.addEventListener('resize', schedule);
            // The in-page A+/A- control changes the root font size without
            // firing resize; observe that style attribute instead. This cannot
            // feed back into apply(), which only touches the nav elements.
            if (window.MutationObserver) {
                var mo = new MutationObserver(schedule);
                [document.documentElement, document.body].forEach(function (el) {
                    if (el) mo.observe(el, { attributes: true, attributeFilter: ['style', 'class'] });
                });
            }
            if (document.fonts && document.fonts.ready) {
                document.fonts.ready.then(schedule);
            }
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
