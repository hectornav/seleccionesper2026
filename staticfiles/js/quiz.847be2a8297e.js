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

function escapeHtml(text) {
    const el = document.createElement('span');
    el.textContent = text;
    return el.innerHTML;
}

function renderResultados(resultados) {
    const container = document.getElementById('resultados-container');
    container.innerHTML = '';

    resultados.forEach((r, i) => {
        const isTop = i === 0;
        const color = r.color_partido || '#D91023';

        // Brújula de Confianza HTML
        const transColor = r.transparencia >= 60 ? '#10b981' : r.transparencia >= 30 ? '#f59e0b' : '#ef4444';
        const antiCorColor = r.score_anticorrupcion >= 7 ? '#10b981' : r.score_anticorrupcion >= 4 ? '#f59e0b' : '#ef4444';

        let posicionesHtml = '';
        if (r.posiciones && r.posiciones.length > 0) {
            posicionesHtml = r.posiciones.map(p => {
                const pillBg = p.claro ? '#e0f2fe' : '#f3f4f6';
                const pillColor = p.claro ? '#0369a1' : '#9ca3af';
                const pillBorder = p.claro ? '#bae6fd' : '#e5e7eb';
                return `<span style="display:inline-block;font-size:0.68rem;padding:3px 8px;border-radius:10px;background:${pillBg};color:${pillColor};border:1px solid ${pillBorder};margin:2px;word-break:break-word" title="${escapeHtml(p.valor)}">${p.label}: <strong>${p.claro ? escapeHtml(p.valor) : '🤐'}</strong></span>`;
            }).join('');
        }

        let alertaHtml = '';
        if (r.tiene_antecedentes) {
            alertaHtml = `<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:6px 10px;font-size:0.72rem;color:#991b1b;margin-top:8px">
                <strong>⚠️ Antecedentes:</strong> ${escapeHtml(r.antecedentes_texto)}
            </div>`;
        }

        const brujulaHtml = `
            <div class="brujula-confianza" style="margin-top:12px;padding-top:12px;border-top:1px dashed #e5e7eb;overflow:hidden">
                <div style="font-size:0.72rem;font-weight:700;color:var(--dark);margin-bottom:8px">🧭 Brújula de Confianza</div>
                <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px">
                    <div style="flex:1;min-width:120px">
                        <div style="font-size:0.68rem;color:#6b7280;margin-bottom:3px">Transparencia</div>
                        <div style="background:#f3f4f6;border-radius:6px;height:8px;overflow:hidden">
                            <div style="width:${r.transparencia}%;height:100%;background:${transColor};border-radius:6px;transition:width 0.6s ease"></div>
                        </div>
                        <div style="font-size:0.65rem;color:${transColor};font-weight:600;margin-top:2px">${r.transparencia}% de temas claros</div>
                    </div>
                    <div style="flex:1;min-width:120px">
                        <div style="font-size:0.68rem;color:#6b7280;margin-bottom:3px">Anticorrupción</div>
                        <div style="background:#f3f4f6;border-radius:6px;height:8px;overflow:hidden">
                            <div style="width:${r.score_anticorrupcion * 10}%;height:100%;background:${antiCorColor};border-radius:6px;transition:width 0.6s ease"></div>
                        </div>
                        <div style="font-size:0.65rem;color:${antiCorColor};font-weight:600;margin-top:2px">${r.score_anticorrupcion}/10</div>
                    </div>
                </div>
                ${alertaHtml}
                ${posicionesHtml ? `<div style="margin-top:8px"><div style="font-size:0.68rem;color:#6b7280;margin-bottom:4px">Posiciones clave:</div><div style="line-height:2">${posicionesHtml}</div></div>` : ''}
                ${r.experiencia ? `<div style="font-size:0.68rem;color:#6b7280;margin-top:6px;word-break:break-word"><strong>Experiencia:</strong> ${escapeHtml(r.experiencia)}</div>` : ''}
                ${r.formacion && r.formacion.length ? `<div style="font-size:0.68rem;color:#6b7280;margin-top:4px"><strong><i class="bi bi-mortarboard"></i> Formación:</strong> ${r.formacion.map(f => escapeHtml(f)).join(' · ')}</div>` : ''}
                ${r.tiene_sentencias_jne ? `<div style="font-size:0.68rem;color:#dc2626;margin-top:4px;font-weight:600"><i class="bi bi-exclamation-triangle-fill"></i> Registra sentencias en su Hoja de Vida JNE</div>` : ''}
            </div>
        `;

        // Ejes del Plan de Gobierno (JNE)
        let ejesHtml = '';
        if (r.ejes_plan && r.ejes_plan.length) {
            ejesHtml = '<div style="margin-top:10px;padding-top:10px;border-top:1px dashed #e5e7eb">' +
                '<div style="font-size:0.72rem;font-weight:700;color:var(--dark);margin-bottom:6px"><i class="bi bi-journal-text"></i> Plan de Gobierno (JNE)</div>' +
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px">' +
                r.ejes_plan.map(e => `<div style="font-size:0.65rem;padding:4px 6px;background:#f8fafc;border-radius:4px;border-left:3px solid ${e.dim==='Social'?'#e11d48':e.dim==='Económica'?'#2563eb':e.dim==='Ambiental'?'#16a34a':'#9333ea'}"><strong>${escapeHtml(e.dim)}:</strong> ${escapeHtml(e.objetivo)}</div>`).join('') +
                '</div>' +
                (r.plan_pdf ? `<a href="${r.plan_pdf}" target="_blank" rel="noopener" style="font-size:0.65rem;color:#3b82f6;text-decoration:none;margin-top:4px;display:inline-block"><i class="bi bi-file-pdf"></i> Ver plan completo</a>` : '') +
                '</div>';
        }

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
            ${brujulaHtml}
            ${ejesHtml}
            <div class="mt-2">
                <a href="/candidato/${r.slug}/" class="btn-peru" style="font-size:0.78rem;padding:0.3rem 0.7rem">
                    <i class="bi bi-eye"></i> Ver perfil completo
                </a>
            </div>
        `;
        container.appendChild(el);
    });

    // Share bar after results
    const shareDiv = document.createElement('div');
    shareDiv.className = 'share-bar mt-4 justify-content-center';
    shareDiv.style.cssText = 'padding:1rem;background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0';
    const topName = resultados[0] ? resultados[0].nombre : '';
    // Save quiz result to localStorage for personalized sharing on home
    if (topName) {
        localStorage.setItem('quiz_resultado_nombre', topName);
    }
    const shareText = topName ? `Mi candidato más afín es ${topName}. Haz el Test Electoral y descubre el tuyo` : 'Haz el Test Electoral — Elecciones Perú 2026';
    shareDiv.innerHTML = `
        <span class="share-label" style="width:100%;text-align:center;display:block;margin-bottom:8px;font-size:0.85rem">
            <i class="bi bi-megaphone"></i> Comparte tu resultado y anima a otros a votar informados
        </span>
        <div class="d-flex flex-wrap gap-2 justify-content-center">
            <button class="share-btn wa" onclick="shareOn('whatsapp','${shareText.replace(/'/g,"\\'")}')">
                <i class="bi bi-whatsapp"></i> <span class="share-text">WhatsApp</span>
            </button>
            <button class="share-btn fb" onclick="shareOn('facebook')">
                <i class="bi bi-facebook"></i> <span class="share-text">Facebook</span>
            </button>
            <button class="share-btn tw" onclick="shareOn('twitter','${shareText.replace(/'/g,"\\'")}')">
                <i class="bi bi-twitter-x"></i> <span class="share-text">X</span>
            </button>
            <button class="share-btn tt" onclick="shareOn('tiktok')">
                <i class="bi bi-tiktok"></i> <span class="share-text">TikTok</span>
            </button>
            <button class="share-btn copy-link" onclick="shareOn('copy')">
                <i class="bi bi-link-45deg"></i> <span class="share-text">Copiar link</span>
            </button>
        </div>
    `;
    container.appendChild(shareDiv);

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
