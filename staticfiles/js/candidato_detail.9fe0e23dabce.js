function showTab(tab) {
        document.querySelectorAll('.tab-content-pane').forEach(el => el.classList.add('d-none'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

        document.getElementById('content-' + tab).classList.remove('d-none');
        document.getElementById('tab-' + tab).classList.add('active');
    }

    function votarDesdeDetalle(candidatoId) {
        const btn = document.getElementById('voteBtn');
        if (btn && btn.disabled) return;

        fetch(`/votacion/votar/${candidatoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
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
            .catch(err => {
                alert('Ocurrió un error al procesar tu voto.');
                console.error(err);
            });
    }