(function () {
    'use strict';

    function closeDrawer() {
        var overlay = document.querySelector('.whale-drawer-overlay');
        var drawer = document.querySelector('.whale-drawer');
        if (overlay) overlay.classList.remove('is-visible');
        if (drawer) drawer.classList.remove('is-visible');
        document.body.classList.remove('whale-drawer-open');
        setTimeout(function () {
            if (overlay) overlay.remove();
            if (drawer) drawer.remove();
        }, 280);
    }

    function openDrawer(url, title) {
        closeDrawer();

        var overlay = document.createElement('div');
        overlay.className = 'whale-drawer-overlay';

        var drawer = document.createElement('div');
        drawer.className = 'whale-drawer';

        var header = document.createElement('div');
        header.className = 'whale-drawer__header';

        var heading = document.createElement('h2');
        heading.textContent = title || 'Добавить';

        var closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'whale-drawer__close';
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Закрыть');
        closeBtn.addEventListener('click', closeDrawer);

        header.appendChild(heading);
        header.appendChild(closeBtn);

        var body = document.createElement('div');
        body.className = 'whale-drawer__body';

        var iframe = document.createElement('iframe');
        var separator = url.indexOf('?') >= 0 ? '&' : '?';
        iframe.src = url + separator + '_drawer=1';
        iframe.title = title || 'Форма';

        body.appendChild(iframe);
        drawer.appendChild(header);
        drawer.appendChild(body);

        document.body.appendChild(overlay);
        document.body.appendChild(drawer);
        document.body.classList.add('whale-drawer-open');

        overlay.addEventListener('click', closeDrawer);

        requestAnimationFrame(function () {
            overlay.classList.add('is-visible');
            drawer.classList.add('is-visible');
        });
    }

    window.addEventListener('message', function (event) {
        if (event.data && event.data.type === 'whale-drawer-close') {
            closeDrawer();
            if (event.data.success) {
                window.location.reload();
            }
        }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeDrawer();
        }
    });

    document.addEventListener('DOMContentLoaded', function () {
        if (!document.body.classList.contains('change-list')) {
            return;
        }
        if (document.body.classList.contains('model-product')) {
            return;
        }
        if (document.body.dataset.drawerAdd !== 'true') {
            return;
        }

        var addLink = document.querySelector('.object-tools a.addlink');
        if (!addLink) {
            return;
        }

        var title = document.querySelector('.content-header h1, .content-header .m-0');
        var drawerTitle = title ? 'Добавить' : 'Добавить';

        addLink.addEventListener('click', function (event) {
            event.preventDefault();
            openDrawer(addLink.href, drawerTitle);
        });
    });

    // Jazzmin related-object modal (+): force iframe to fill the modal body
    if (window.jQuery && document.body.className.indexOf('popup') === -1) {
        (function ($) {
            function fixRelatedModalIframe() {
                $('iframe.related-iframe, #related-modal-iframe').each(function () {
                    this.style.display = 'block';
                    this.style.width = '100%';
                    this.style.minWidth = '100%';
                    this.style.height = '520px';
                    this.style.minHeight = '520px';
                    this.style.border = 'none';
                });
            }

            $(document).on('shown.bs.modal', '[class*="related-modal-"]', fixRelatedModalIframe);
            $(document).on('click', 'a.related-widget-wrapper-link, a.related-lookup', function () {
                setTimeout(fixRelatedModalIframe, 50);
                setTimeout(fixRelatedModalIframe, 300);
            });
        })(jQuery);
    }
})();
