/**
 * Site Controls for Stack Teller Trust Bank
 * Handles Light/Dark theme toggle and Google Translate widget integration.
 */

(function() {
    // 0. Inject PWA Manifest & Service Worker Registration dynamically
    if (!document.querySelector('link[rel="manifest"]')) {
        var linkManifest = document.createElement('link');
        linkManifest.rel = 'manifest';
        linkManifest.href = '/manifest.json';
        document.head.appendChild(linkManifest);
    }
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(reg) {
                    console.log('✅ PWA Service Worker Registered:', reg.scope);
                })
                .catch(function(err) {
                    console.warn('❌ PWA Service Worker Registration failed:', err);
                });
        });
    }

    // 1. Ensure Font Awesome is loaded for icons
    if (!document.querySelector('link[href*="font-awesome"]') && !document.querySelector('link[href*="all.min.css"]') && !document.querySelector('link[href*="all.css"]')) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(link);
    }

    // 2. Inject Light Theme CSS overrides dynamically
    var style = document.createElement('style');
    style.id = 'theme-override-styles';
    style.innerHTML = `
        /* Floating Site Controls Widget */
        .site-controls-pill {
            position: fixed;
            top: 100px;
            right: 20px;
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 15px;
            z-index: 99999;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: all 0.3s ease;
        }
        .control-item {
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            transition: all 0.2s ease;
        }
        .control-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.05);
        }
        .translate-wrapper {
            position: relative;
            background: transparent !important;
            width: auto;
            height: auto;
            border-radius: 0;
        }
        
        /* Google Translate Gadget Styling */
        #google_translate_element {
            display: inline-block;
            vertical-align: middle;
        }
        .goog-te-gadget-simple {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            padding: 4px 8px !important;
            border-radius: 20px !important;
            font-size: 11px !important;
            color: #ffffff !important;
            cursor: pointer;
            font-family: inherit !important;
        }
        .goog-te-gadget-simple img {
            display: none !important;
        }
        .goog-te-gadget-simple span {
            color: #ffffff !important;
        }
        .goog-te-menu-value span {
            color: #ffffff !important;
        }
        .goog-te-menu-frame {
            box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
        }

        /* LIGHT THEME OVERRIDES (Active when body has .light-theme) */
        body.light-theme {
            background: #f8fafc !important;
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        
        body.light-theme, 
        body.light-theme p, 
        body.light-theme span, 
        body.light-theme h1, 
        body.light-theme h2, 
        body.light-theme h3, 
        body.light-theme h4, 
        body.light-theme h5, 
        body.light-theme h6, 
        body.light-theme li, 
        body.light-theme td, 
        body.light-theme th,
        body.light-theme div:not(.goog-te-gadget-simple):not(.payment-icon):not(.crypto-card-header):not(.address-value):not(.welcome-section) {
            color: #1e293b !important;
        }

        body.light-theme .site-controls-pill {
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        }
        body.light-theme .control-item {
            background: rgba(0, 0, 0, 0.05);
            color: #1e293b;
        }
        body.light-theme .control-item:hover {
            background: rgba(0, 0, 0, 0.1);
        }
        body.light-theme .goog-te-gadget-simple {
            background-color: rgba(0, 0, 0, 0.05) !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
        }
        body.light-theme .goog-te-gadget-simple span,
        body.light-theme .goog-te-menu-value span {
            color: #1e293b !important;
        }

        /* Layout Component Overrides */
        body.light-theme .login-container,
        body.light-theme .account-card,
        body.light-theme .balance-card,
        body.light-theme .card,
        body.light-theme .modal-content,
        body.light-theme .transaction-card,
        body.light-theme .loan-card,
        body.light-theme .investment-card,
        body.light-theme .popup-content,
        body.light-theme .crypto-card,
        body.light-theme .info-box,
        body.light-theme .detail-row {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
        }

        body.light-theme .bank-header {
            background: #ffffff !important;
            border-bottom: 1px solid #e2e8f0 !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03) !important;
        }
        body.light-theme .bank-header h1,
        body.light-theme .bank-header h1 i,
        body.light-theme .nav-toggle {
            color: #1e293b !important;
        }
        
        body.light-theme .nav-sidebar {
            background: #ffffff !important;
            border-left: 1px solid #e2e8f0 !important;
        }
        body.light-theme .sidebar-header {
            background: #f1f5f9 !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        body.light-theme .sidebar-close {
            color: #64748b !important;
        }
        body.light-theme .nav-menu a {
            color: #475569 !important;
        }
        body.light-theme .nav-menu a:hover,
        body.light-theme .nav-menu a.active {
            background: #f1f5f9 !important;
            color: #0f172a !important;
        }
        body.light-theme .user-details {
            border-bottom: 1px solid #e2e8f0 !important;
            background: #f8fafc !important;
        }
        
        body.light-theme .account-number-section,
        body.light-theme .payment-icon,
        body.light-theme .info-value-wrapper {
            background: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
        }

        body.light-theme .form-control,
        body.light-theme input,
        body.light-theme select,
        body.light-theme textarea {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #0f172a !important;
        }
        body.light-theme .form-control:focus {
            border-color: #94a3b8 !important;
            box-shadow: 0 0 0 2px rgba(148, 163, 184, 0.1) !important;
        }

        body.light-theme .transactions-table th {
            background-color: #f1f5f9 !important;
            border-bottom: 2px solid #e2e8f0 !important;
        }
        body.light-theme .transactions-table td {
            border-bottom: 1px solid #e2e8f0 !important;
        }

        body.light-theme .bottom-navbar {
            background: #ffffff !important;
            border-top: 1px solid #e2e8f0 !important;
            box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.03) !important;
        }
        body.light-theme .nav-link {
            color: #64748b !important;
        }
        body.light-theme .nav-link.active,
        body.light-theme .nav-link:hover {
            color: #00e676 !important;
        }
        body.light-theme .nav-link.active i,
        body.light-theme .nav-link:hover i {
            color: #00e676 !important;
        }

        body.light-theme a {
            color: #3b82f6 !important;
        }
        body.light-theme a:hover {
            color: #1d4ed8 !important;
        }
        
        body.light-theme .btn-primary,
        body.light-theme .login-btn,
        body.light-theme .submit-btn {
            background: #0f172a !important;
            color: #ffffff !important;
            border: 1px solid #0f172a !important;
        }
        body.light-theme .btn-primary:hover,
        body.light-theme .login-btn:hover,
        body.light-theme .submit-btn:hover {
            background: #1e293b !important;
            border-color: #1e293b !important;
        }
        
        /* Exclude Dashboard account gradient card from light mode theme modifications */
        body.light-theme .account-card-grad,
        body.light-theme .account-card-grad * {
            background: inherit !important;
            color: inherit !important;
            border-color: inherit !important;
        }

        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
            .site-controls-pill {
                top: 15px;
                right: 15px;
                padding: 6px 12px !important;
                gap: 8px !important;
            }
            .goog-te-menu-frame {
                max-width: 90vw !important;
                left: auto !important;
                right: 15px !important;
                top: 60px !important;
            }
            .goog-te-gadget-simple {
                padding: 2px 6px !important;
            }
        }

        /* Hide Telegram and Email support floats site-wide */
        .telegram-float, .email-float, .telegram-link, .email-link, #telegramBtn, #emailBtn {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    // 3. Setup Google Translate functions globally
    window.googleTranslateElementInit = function() {
        new google.translate.TranslateElement({
            pageLanguage: 'en',
            layout: google.translate.TranslateElement.InlineLayout.SIMPLE
        }, 'google_translate_element');
    };

    // 4. Create and inject the floating widget
    document.addEventListener("DOMContentLoaded", function() {
        // Render custom SVG logo inside all logo icons
        var logoIcons = document.querySelectorAll('.logo-icon');
        logoIcons.forEach(function(icon) {
            icon.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="100%" height="100%">
                  <defs>
                    <linearGradient id="blockGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#00C853" />
                      <stop offset="100%" stop-color="#0070F3" />
                    </linearGradient>
                  </defs>
                  <g transform="translate(16, 16) scale(0.9)">
                    <!-- Bottom block -->
                    <path d="M 16 160 L 112 200 L 208 160 L 112 120 Z" fill="url(#blockGrad)" opacity="0.5" />
                    <path d="M 16 160 L 16 172 L 112 212 L 112 200 Z" fill="#004D20" opacity="0.4" />
                    <path d="M 112 200 L 112 212 L 208 172 L 208 160 Z" fill="#002D80" opacity="0.4" />

                    <!-- Middle block -->
                    <path d="M 16 110 L 112 150 L 208 110 L 112 70 Z" fill="url(#blockGrad)" opacity="0.8" />
                    <path d="M 16 110 L 16 122 L 112 162 L 112 150 Z" fill="#004D20" opacity="0.5" />
                    <path d="M 112 150 L 112 162 L 208 122 L 208 110 Z" fill="#002D80" opacity="0.5" />

                    <!-- Top block -->
                    <path d="M 16 60 L 112 100 L 208 60 L 112 20 Z" fill="url(#blockGrad)" />
                    <path d="M 16 60 L 16 72 L 112 112 L 112 100 Z" fill="#004D20" opacity="0.6" />
                    <path d="M 112 100 L 112 112 L 208 72 L 208 60 Z" fill="#002D80" opacity="0.6" />
                  </g>
                </svg>
            `;
            icon.style.background = 'transparent';
            icon.style.border = 'none';
            icon.style.display = 'inline-flex';
            icon.style.alignItems = 'center';
            icon.style.justifyContent = 'center';
        });

        // Create widget container
        var widget = document.createElement('div');
        widget.id = 'site-controls-widget';
        widget.className = 'site-controls-pill';
        
        widget.innerHTML = `
            <div class="control-item theme-toggle" id="theme-toggle-btn" title="Toggle Theme">
                <i id="site-theme-icon" class="fas fa-moon"></i>
            </div>
            <div class="control-item translate-wrapper">
                <div id="google_translate_element"></div>
            </div>
        `;
        document.body.appendChild(widget);

        // Load Google Translate script
        var s = document.createElement('script');
        s.type = 'text/javascript';
        s.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
        document.body.appendChild(s);

        // Bind theme toggle event
        var toggleBtn = document.getElementById('theme-toggle-btn');
        var themeIcon = document.getElementById('site-theme-icon');

        function applyTheme(theme) {
            if (theme === 'light') {
                document.body.classList.add('light-theme');
                if (themeIcon) {
                    themeIcon.className = 'fas fa-sun';
                }
            } else {
                document.body.classList.remove('light-theme');
                if (themeIcon) {
                    themeIcon.className = 'fas fa-moon';
                }
            }
        }

        // Initialize theme from LocalStorage
        var savedTheme = localStorage.getItem('site-theme') || 'dark';
        applyTheme(savedTheme);

        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                var currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
                var newTheme = currentTheme === 'light' ? 'dark' : 'light';
                localStorage.setItem('site-theme', newTheme);
                applyTheme(newTheme);
            });
        }

        // Draggable site controls widget (long press to drag)
        var draggableWidget = document.getElementById('site-controls-widget');
        if (draggableWidget) {
            var isDragging = false;
            var dragTimeout = null;
            var startX = 0;
            var startY = 0;
            var initialX = 0;
            var initialY = 0;

            function onStart(e) {
                if (e.type === 'mousedown' && e.button !== 0) return;

                var clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
                var clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;

                startX = clientX;
                startY = clientY;

                var rect = draggableWidget.getBoundingClientRect();
                initialX = rect.left;
                initialY = rect.top;

                dragTimeout = setTimeout(function() {
                    isDragging = true;
                    draggableWidget.style.transform = 'scale(1.1)';
                    draggableWidget.style.border = '1px solid #00C853';
                    draggableWidget.style.cursor = 'move';
                    draggableWidget.style.boxShadow = '0 0 15px rgba(0, 200, 83, 0.6)';
                    
                    if (navigator.vibrate) {
                        navigator.vibrate(50);
                    }
                }, 500);

                window.addEventListener(e.type === 'touchstart' ? 'touchmove' : 'mousemove', onMove, { passive: false });
                window.addEventListener(e.type === 'touchstart' ? 'touchend' : 'mouseup', onEnd);
            }

            function onMove(e) {
                var clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
                var clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;

                if (!isDragging) {
                    if (Math.abs(clientX - startX) > 5 || Math.abs(clientY - startY) > 5) {
                        clearTimeout(dragTimeout);
                    }
                    return;
                }

                e.preventDefault();
                var dx = clientX - startX;
                var dy = clientY - startY;

                var newLeft = initialX + dx;
                var newTop = initialY + dy;

                var padding = 10;
                newLeft = Math.max(padding, Math.min(newLeft, window.innerWidth - draggableWidget.offsetWidth - padding));
                newTop = Math.max(padding, Math.min(newTop, window.innerHeight - draggableWidget.offsetHeight - padding));

                draggableWidget.style.left = newLeft + 'px';
                draggableWidget.style.top = newTop + 'px';
                draggableWidget.style.right = 'auto';
                draggableWidget.style.bottom = 'auto';
            }

            function onEnd() {
                clearTimeout(dragTimeout);
                if (isDragging) {
                    isDragging = false;
                    draggableWidget.style.transform = 'none';
                    draggableWidget.style.border = '1px solid rgba(255, 255, 255, 0.1)';
                    draggableWidget.style.cursor = 'pointer';
                    draggableWidget.style.boxShadow = '0 8px 32px 0 rgba(0, 0, 0, 0.37)';
                    
                    localStorage.setItem('widget-pos-left', draggableWidget.style.left);
                    localStorage.setItem('widget-pos-top', draggableWidget.style.top);
                }

                window.removeEventListener('mousemove', onMove);
                window.removeEventListener('touchmove', onMove);
                window.removeEventListener('mouseup', onEnd);
                window.removeEventListener('touchend', onEnd);
            }

            var savedLeft = localStorage.getItem('widget-pos-left');
            var savedTop = localStorage.getItem('widget-pos-top');
            if (savedLeft && savedTop) {
                draggableWidget.style.left = savedLeft;
                draggableWidget.style.top = savedTop;
                draggableWidget.style.right = 'auto';
                draggableWidget.style.bottom = 'auto';
                draggableWidget.style.position = 'fixed';
            }

            draggableWidget.addEventListener('mousedown', onStart);
            draggableWidget.addEventListener('touchstart', onStart, { passive: true });
        }
    });
})();
