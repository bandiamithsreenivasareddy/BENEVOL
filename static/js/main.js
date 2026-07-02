/* BENEVOL - Main JavaScript */

function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    try { localStorage.setItem('benevol-theme', theme); } catch (e) {}
    const icon = document.getElementById('themeIcon');
    const label = document.getElementById('themeLabel');
    const sw = document.getElementById('themeSwitch');
    if (icon)  icon.className = (theme === 'dark' ? 'bi bi-sun me-2' : 'bi bi-moon-stars me-2');
    if (label) label.textContent = (theme === 'dark' ? 'Light Mode' : 'Dark Mode');
    if (sw)    sw.checked = (theme === 'dark');
}

function toggleTheme(e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
}

document.addEventListener('DOMContentLoaded', function() {

    // Initialize theme state in the dropdown
    const saved = (function(){ try { return localStorage.getItem('benevol-theme'); } catch (e) { return null; } })() || 'light';
    applyTheme(saved);


    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Image preview on file input
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Confirm delete
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar .nav-link').forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Tooltip initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });

});