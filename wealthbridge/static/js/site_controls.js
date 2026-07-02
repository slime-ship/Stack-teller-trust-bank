/**
 * Site Controls for Stack Teller Trust Bank
 * Handles Light/Dark theme toggle and Google Translate widget integration.
 */

(function() {
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
    });
})();
