function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    menu.classList.toggle('d-none');
}

function shareOn(platform, customText) {
    var url = encodeURIComponent(window.location.href);
    var text = encodeURIComponent(customText || document.title);
    var shareUrl = '';

    switch (platform) {
        case 'facebook':
            shareUrl = 'https://www.facebook.com/sharer/sharer.php?u=' + url;
            break;
        case 'whatsapp':
            shareUrl = 'https://api.whatsapp.com/send?text=' + text + '%20' + url;
            break;
        case 'twitter':
            shareUrl = 'https://twitter.com/intent/tweet?text=' + text + '&url=' + url;
            break;
        case 'tiktok':
            // TikTok doesn't have a direct share URL, copy to clipboard for sharing
            copyShareLink();
            return;
        case 'copy':
            copyShareLink();
            return;
    }
    if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=500,noopener');
    }
}

function copyShareLink() {
    navigator.clipboard.writeText(window.location.href).then(function () {
        var btn = document.querySelector('.share-btn.copy-link');
        if (btn) {
            var orig = btn.innerHTML;
            btn.innerHTML = '<i class="bi bi-check2"></i> <span class="share-text">Copiado</span>';
            setTimeout(function () { btn.innerHTML = orig; }, 2000);
        }
    });
}
