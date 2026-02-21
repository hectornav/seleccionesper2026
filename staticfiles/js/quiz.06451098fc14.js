const totalPreguntas = parseInt(document.getElementById('quiz-data').dataset.total, 10);
let preguntaActual = 1;
let respuestas = {};

function iniciarQuiz() {
    document.getElementById('quiz-intro').classList.add('d-none');
    document.getElementById('quiz-preguntas').classList.remove('d-none');
    mostrarPregunta(1);
}

function mostrarPregunta(num) {
    document.querySelectorAll('.pregunta-card').forEach(el => el.classList.add('d-none'));
    const card = document.querySelector(`.pregunta-card[data-pregunta="${num}"]`);
    if (card) {
        card.classList.remove('d-none');
        // Restaurar selección si ya respondió
        const pregId = card.dataset.preguntaId;
        if (respuestas[pregId] !== undefined) {
            card.querySelectorAll('.opcion-btn').forEach(btn => {
                if (parseInt(btn.dataset.valor) === respuestas[pregId]) {
                    btn.classList.add('selected');
                    btn.querySelector('.opcion-num').style.background = 'var(--peru-red)';
                    btn.querySelector('.opcion-num').style.color = 'white';
                }
            });
            // Habilitar botón siguiente
            const sigBtn = card.querySelector('.sig-btn');
            if (sigBtn) {
                sigBtn.disabled = false;
                sigBtn.style.opacity = '1';
                sigBtn.style.cursor = 'pointer';
            }
        }
    }
    actualizarProgreso(num);
}

function actualizarProgreso(num) {
    const pct = Math.round((num - 1) / totalPreguntas * 100);
    document.getElementById('progress-text').textContent = `${num} / ${totalPreguntas}`;
    document.getElementById('progress-bar').style.width = pct + '%';
    document.getElementById('progress-pct').textContent = pct + '%';
}

function seleccionarOpcion(btn, valor, preguntaId) {
    const card = btn.closest('.pregunta-card');
    // Desmarcar todas
    card.querySelectorAll('.opcion-btn').forEach(b => {
        b.classList.remove('selected');
        b.querySelector('.opcion-num').style.background = '#e9ecef';
        b.querySelector('.opcion-num').style.color = '';
    });
    // Marcar seleccionada
    btn.classList.add('selected');
    btn.querySelector('.opcion-num').style.background = 'var(--peru-red)';
    btn.querySelector('.opcion-num').style.color = 'white';
    // Guardar respuesta
    respuestas[preguntaId] = valor;
    // Habilitar siguiente
    const sigBtn = card.querySelector('.sig-btn');
    if (sigBtn) {
        sigBtn.disabled = false;
        sigBtn.style.opacity = '1';
        sigBtn.style.cursor = 'pointer';
    }
}

function siguientePregunta(btn) {
    const card = btn.closest('.pregunta-card');
    const total = parseInt(card.dataset.total);
    if (preguntaActual < total) {
        preguntaActual++;
        mostrarPregunta(preguntaActual);
    }
}

function anteriorPregunta() {
    if (preguntaActual > 1) {
        preguntaActual--;
        mostrarPregunta(preguntaActual);
    }
}

async function verResultados() {
    document.getElementById('quiz-preguntas').classList.add('d-none');
    document.getElementById('quiz-loading').classList.remove('d-none');

    const quizData = document.getElementById('quiz-data');
    try {
        const response = await fetch(quizData.dataset.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': quizData.dataset.csrf
            },
            body: JSON.stringify({ respuestas })
        });

        const data = await response.json();
        document.getElementById('quiz-loading').classList.add('d-none');
        document.getElementById('quiz-resultados').classList.remove('d-none');
        renderResultados(data.resultados);
    } catch (e) {
        document.getElementById('quiz-loading').classList.add('d-none');
        alert('Error calculando resultados. Intenta de nuevo.');
    }
}

function renderResultados(resultados) {
    const container = document.getElementById('resultados-container');
    container.innerHTML = '';

    resultados.forEach((r, i) => {
        const isTop = i === 0;
        const color = r.color_partido || '#D91023';

        const el = document.createElement('div');
        el.className = `resultado-card mb-3 ${isTop ? 'top-1' : ''}`;
        el.style.animation = `fadeInUp 0.4s ease ${i * 0.1}s both`;
        el.innerHTML = `
            <div style="display:flex;align-items:center;gap:12px">
                ${isTop ? '<div style="font-size:1.5rem;flex-shrink:0">🥇</div>' : `<div style="width:28px;height:28px;border-radius:50%;background:#e9ecef;display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:800;color:#6c757d;flex-shrink:0">${i + 1}</div>`}

                ${r.foto_url ? `<img src="${r.foto_url}" alt="${r.nombre}" style="width:${isTop ? 56 : 44}px;height:${isTop ? 64 : 52}px;border-radius:10px;object-fit:cover;object-position:top;flex-shrink:0;border:2px solid ${isTop ? 'var(--gold)' : '#e9ecef'}">` :
                `<div style="width:${isTop ? 56 : 44}px;height:${isTop ? 64 : 52}px;border-radius:10px;background:#e9ecef;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:${isTop ? 28 : 22}px;color:#adb5bd"><i class='bi bi-person-fill'></i></div>`}

                <div style="flex:1;min-width:0">
                    <div style="font-weight:${isTop ? 800 : 700};font-size:${isTop ? '1rem' : '0.9rem'};color:var(--dark)">${r.nombre}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted-custom);margin-bottom:6px">
                        <span style="background:${color};color:white;border-radius:20px;padding:1px 8px;font-size:0.7rem">${r.partido}</span>
                        &bull; ${r.posicion}
                    </div>
                    <div class="match-bar">
                        <div class="match-bar-fill" style="width:0%;background:${isTop ? 'linear-gradient(to right,var(--gold),#e8960f)' : 'linear-gradient(to right,var(--peru-red),var(--gold))'}"
                             data-width="${r.porcentaje}%"></div>
                    </div>
                </div>
                <div style="text-align:center;flex-shrink:0;min-width:50px">
                    <div style="font-size:${isTop ? '1.5rem' : '1.2rem'};font-weight:800;color:${isTop ? 'var(--gold)' : 'var(--peru-red)'}">${r.porcentaje}%</div>
                    <div style="font-size:0.65rem;color:var(--text-muted-custom)">afinidad</div>
                </div>
            </div>
            ${r.lema ? `<p style="font-size:0.78rem;font-style:italic;color:#4a5568;margin:0.75rem 0 0;border-left:3px solid ${isTop ? 'var(--gold)' : 'var(--peru-red)'};padding-left:0.6rem">"${r.lema}"</p>` : ''}
            <div class="mt-2">
                <a href="/candidato/${r.slug}/" class="btn-peru" style="font-size:0.78rem;padding:0.3rem 0.7rem">
                    <i class="bi bi-eye"></i> Ver propuestas
                </a>
            </div>
        `;
        container.appendChild(el);
    });

    // Animar barras
    setTimeout(() => {
        document.querySelectorAll('.match-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.width;
        });
    }, 100);
}

function reiniciarQuiz() {
    preguntaActual = 1;
    respuestas = {};
    document.querySelectorAll('.opcion-btn').forEach(btn => {
        btn.classList.remove('selected');
        btn.querySelector('.opcion-num').style.background = '#e9ecef';
        btn.querySelector('.opcion-num').style.color = '';
    });
    document.querySelectorAll('.sig-btn').forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.style.cursor = 'not-allowed';
    });
    document.getElementById('quiz-resultados').classList.add('d-none');
    document.getElementById('quiz-intro').classList.remove('d-none');
}
