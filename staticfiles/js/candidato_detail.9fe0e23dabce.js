function showTab(tab) {
        document.querySelectorAll('.tab-content-pane').forEach(el => el.classList.add('d-none'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

        document.getElementById('content-' + tab).classList.remove('d-none');
        document.getElementById('tab-' + tab).classList.add('active');
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function votarDesdeDetalle(candidatoId) {
        const btn = document.getElementById('voteBtn');
        if (btn && btn.disabled) return;
        let csrftoken = getCookie('csrftoken');
        if (!csrftoken) {
            const el = document.getElementById('vote-csrf');
            if (el) csrftoken = el.dataset.csrf;
        }

        fetch(`/votacion/votar/${candidatoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (btn) {
                        btn.disabled = true;
                        btn.innerHTML = '<i class="bi bi-check-circle-fill"></i> ¡Voto registrado!';
                        btn.style.background = '#27ae60';
                        btn.style.borderColor = '#27ae60';
                        btn.style.color = 'white';
                    }
                } else {
                    alert(data.message);
                }
            })
            .catch(async err => {
                console.error('Fetch error:', err);
                let text;
                try {
                    const resText = await err?.response?.text?.();
                    text = resText || '';
                } catch (e) {
                    text = '';
                }
                alert('Ocurrió un error al procesar tu voto. Revisa la consola para más detalles.');
            });
    }