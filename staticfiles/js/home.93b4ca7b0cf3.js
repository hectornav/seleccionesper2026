const searchInput = document.getElementById('search-input');
    const posicionFilter = document.getElementById('posicion-filter');
    const partidoFilter = document.getElementById('partido-filter');
    const candidatoItems = document.querySelectorAll('.candidato-item');
    const noResults = document.getElementById('no-results');
    const candidatosGrid = document.getElementById('candidatos-grid');
    const countDisplay = document.querySelector('.section-title + span') || document.createElement('span');

    function filterCandidatos() {
        const query = searchInput.value.toLowerCase().trim();
        const posicion = posicionFilter.value;
        const partido = partidoFilter.value;
        let visibleCount = 0;

        candidatoItems.forEach(item => {
            const matchesSearch = item.dataset.nombre.includes(query);
            const matchesPosicion = !posicion || item.dataset.posicion === posicion;
            const matchesPartido = !partido || item.dataset.partido === partido;

            if (matchesSearch && matchesPosicion && matchesPartido) {
                item.classList.remove('d-none');
                visibleCount++;
            } else {
                item.classList.add('d-none');
            }
        });

        // Toggle no results message
        if (visibleCount === 0) {
            noResults.classList.remove('d-none');
            if (candidatosGrid) candidatosGrid.classList.add('d-none');
        } else {
            noResults.classList.add('d-none');
            if (candidatosGrid) candidatosGrid.classList.remove('d-none');
        }

        // Update count text
        if (countDisplay) {
            countDisplay.textContent = `${visibleCount} candidato${visibleCount !== 1 ? 's' : ''}`;
        }
    }

    function resetFilters() {
        searchInput.value = '';
        posicionFilter.value = '';
        partidoFilter.value = '';
        filterCandidatos();
    }

    // Attach events
    searchInput.addEventListener('input', filterCandidatos);
    posicionFilter.addEventListener('change', filterCandidatos);
    partidoFilter.addEventListener('change', filterCandidatos);

    // Initial check (in case search query was passed via URL)
    if (searchInput.value || posicionFilter.value || partidoFilter.value) {
        filterCandidatos();
    }