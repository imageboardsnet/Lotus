document.addEventListener('DOMContentLoaded', () => {
    const hero = document.querySelector('.hero');
    const heroClose = document.getElementById('hero-close');

    if (hero) {
        const heroDismissed = document.cookie.split('; ').find(row => row.startsWith('hero_dismissed='));
        if (heroDismissed) {
            hero.remove();
        }

        if (heroClose) {
            heroClose.addEventListener('click', () => {
                document.cookie = `hero_dismissed=true; path=/; max-age=${60 * 60 * 24 * 30}`;
                hero.remove();
            });
        }
    }

    const copyButtons = document.querySelectorAll('.copy-link');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const url = btn.dataset.url;
            try {
                await navigator.clipboard.writeText(url);
                btn.innerHTML = '<i class="bi bi-check2"></i> Copied';
                setTimeout(() => {
                    btn.innerHTML = '<i class="bi bi-clipboard"></i> Copy link';
                }, 1200);
            } catch (e) {
                btn.innerHTML = '<i class="bi bi-x"></i> Failed';
            }
        });
    });

    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        const toggleBtn = () => {
            if (window.scrollY > 260) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        };
        window.addEventListener('scroll', toggleBtn);
        backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
        toggleBtn();
    }

    if (window.bootstrap) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    document.querySelectorAll('.unified-menu .dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            const menu = item.closest('[data-target]');
            const target = menu ? menu.dataset.target : null;
            if (!target) return;
            const value = item.dataset.value || '';
            const hiddenInput = document.getElementById(target);
            const group = item.closest('.btn-group');
            const label = group ? group.querySelector('.dropdown-label') : null;
            if (hiddenInput) hiddenInput.value = value;
            if (label) label.textContent = value || (target === 'language' ? 'Any language' : 'Any software');
        });
    });

    const viewerFrame = document.getElementById('viewer-frame');
    const viewerItems = document.querySelectorAll('.viewer-item');
    const openNew = document.getElementById('open-new');
    if (viewerItems.length) {
        viewerItems.forEach(btn => {
            btn.addEventListener('click', () => {
                const url = btn.dataset.url;
                viewerItems.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                if (viewerFrame) viewerFrame.src = url;
                if (openNew) openNew.href = url;
            });
        });
    }
});
