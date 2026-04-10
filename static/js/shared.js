// ============================================================
//  CONFIGURATION — Update before going live
// ============================================================
const PHONE     = '919217297800';   // WhatsApp: Aum Creations
const API_BASE  = 'http://127.0.0.1:5000/api';  // Your FastAPI backend

// ============================================================
//  UTILITIES
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const yr = document.getElementById('yr');
    if (yr) yr.textContent = new Date().getFullYear();
});

function openWA(msg) {
    window.open(`https://wa.me/${PHONE}?text=${encodeURIComponent(msg)}`, '_blank');
    return false;
}

function scrollToContact() {
    window.location.href = 'contact.html';
}

// ============================================================
//  LANGUAGE TOGGLE
// ============================================================
let lang = localStorage.getItem('lang') || 'en';

function applyLang() {
    const body = document.getElementById('bodyEl');
    const label = document.getElementById('langLabel');
    if (!body) return;
    if (lang === 'hi') {
        body.classList.replace('lang-en', 'lang-hi');
        if (label) label.textContent = 'English';
    } else {
        body.classList.replace('lang-hi', 'lang-en');
        if (label) label.textContent = 'हिंदी';
    }
}

function toggleLang() {
    lang = lang === 'en' ? 'hi' : 'en';
    localStorage.setItem('lang', lang);
    applyLang();
}

document.addEventListener('DOMContentLoaded', applyLang);

// ============================================================
//  MOBILE MENU
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const mmToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.getElementById('navLinks');
    if (mmToggle && navLinks) {
        mmToggle.addEventListener('click', () => navLinks.classList.toggle('active'));
        navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('active')));
    }

    // Scroll to top
    const stt = document.getElementById('scrollToTop');
    if (stt) {
        window.addEventListener('scroll', () => stt.classList.toggle('show', scrollY > 300));
        stt.addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));
    }

    // Animations
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -80px 0px' });

    document.querySelectorAll('.service-card, .feature-card, .testimonial-card, .portfolio-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Mark active nav link
    const page = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(a => {
        if (a.getAttribute('href') === page) a.style.color = 'var(--primary)';
    });
});
