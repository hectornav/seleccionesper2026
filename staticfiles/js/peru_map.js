/**
 * Peru Interactive SVG Map
 * All 25 departments (regions) with approximate boundaries.
 * Usage: initPeruMap('container-id')
 */
function initPeruMap(containerId) {
  var container = document.getElementById(containerId);
  if (!container) return;

  var DEPT_COLOR = '#dbeafe';
  var HOVER_COLOR = '#60a5fa';
  var SELECTED_COLOR = '#3b82f6';
  var STROKE_COLOR = '#94a3b8';
  var SELECTED_STROKE = '#ffffff';

  // Get current department filter from URL
  var urlParams = new URLSearchParams(window.location.search);
  var currentDept = (urlParams.get('departamento') || '').toUpperCase();

  // Departments with approximate SVG polygon paths
  // Viewbox is 0 0 500 700 — Peru roughly fits in this aspect ratio
  // Coordinates are approximate but positioned to be geographically recognizable
  var departments = [
    {
      name: 'TUMBES',
      path: 'M 48,18 L 62,12 78,16 85,28 80,42 68,48 52,44 42,34 Z'
    },
    {
      name: 'PIURA',
      path: 'M 42,34 L 52,44 68,48 80,42 85,28 100,32 118,48 125,68 118,88 100,95 82,92 65,85 50,78 38,65 35,50 Z'
    },
    {
      name: 'LAMBAYEQUE',
      path: 'M 50,78 L 65,85 82,92 100,95 108,108 98,118 80,120 65,112 52,100 48,88 Z'
    },
    {
      name: 'CAJAMARCA',
      path: 'M 100,95 L 118,88 125,68 140,62 160,70 170,85 168,105 158,120 140,128 120,130 108,120 108,108 Z'
    },
    {
      name: 'AMAZONAS',
      path: 'M 140,62 L 160,48 180,42 200,50 210,68 205,88 195,105 178,112 158,120 168,105 170,85 160,70 Z'
    },
    {
      name: 'LORETO',
      path: 'M 160,48 L 180,42 200,50 210,68 205,88 220,78 250,55 280,40 320,30 355,38 380,55 390,80 385,110 370,140 350,165 325,185 300,195 275,200 250,195 230,185 215,170 205,150 200,130 195,105 210,68 200,50 180,42 Z'
    },
    {
      name: 'SAN MARTIN',
      path: 'M 158,120 L 178,112 195,105 200,130 205,150 210,165 200,178 185,185 168,180 152,170 142,155 140,140 140,128 Z'
    },
    {
      name: 'LA LIBERTAD',
      path: 'M 52,100 L 65,112 80,120 98,118 108,108 108,120 120,130 140,128 140,140 132,155 118,162 100,158 82,150 65,140 52,128 48,112 Z'
    },
    {
      name: 'ANCASH',
      path: 'M 48,112 L 52,128 65,140 82,150 100,158 118,162 132,155 138,168 130,182 112,190 92,188 72,180 55,168 45,152 42,135 Z'
    },
    {
      name: 'HUANUCO',
      path: 'M 132,155 L 140,140 142,155 152,170 168,180 185,185 188,198 178,215 162,222 145,218 130,208 122,195 118,182 130,182 Z'
    },
    {
      name: 'PASCO',
      path: 'M 118,182 L 122,195 130,208 145,218 150,232 140,245 125,248 112,240 102,225 98,210 100,195 112,190 Z'
    },
    {
      name: 'UCAYALI',
      path: 'M 185,185 L 200,178 210,165 215,170 230,185 250,195 275,200 300,195 310,210 305,235 295,260 280,280 260,295 240,300 220,295 205,280 195,260 188,240 185,220 178,215 188,198 Z'
    },
    {
      name: 'JUNIN',
      path: 'M 100,195 L 102,225 112,240 125,248 140,245 150,232 145,218 162,222 178,215 185,220 188,240 180,258 165,268 148,272 130,268 115,258 105,245 98,228 95,212 Z'
    },
    {
      name: 'LIMA',
      path: 'M 42,135 L 45,152 55,168 72,180 92,188 100,195 95,212 98,228 92,242 80,252 65,258 50,252 38,238 30,218 28,198 30,178 35,158 Z'
    },
    {
      name: 'CALLAO',
      path: 'M 28,198 L 30,194 36,192 40,198 38,206 32,208 28,204 Z'
    },
    {
      name: 'HUANCAVELICA',
      path: 'M 80,252 L 92,242 98,228 105,245 115,258 130,268 128,282 118,295 102,300 88,295 78,282 72,268 Z'
    },
    {
      name: 'ICA',
      path: 'M 38,238 L 50,252 65,258 80,252 72,268 78,282 72,298 62,312 50,318 38,312 30,298 25,278 28,258 Z'
    },
    {
      name: 'AYACUCHO',
      path: 'M 78,282 L 88,295 102,300 118,295 128,282 130,268 148,272 165,268 172,282 168,300 158,318 142,330 125,335 108,330 95,318 85,305 Z'
    },
    {
      name: 'APURIMAC',
      path: 'M 128,282 L 130,268 148,272 165,268 172,282 165,298 152,305 138,305 128,298 Z'
    },
    {
      name: 'CUSCO',
      path: 'M 165,268 L 180,258 188,240 195,260 205,280 220,295 240,300 248,315 240,335 222,350 200,358 180,355 162,345 148,335 142,330 158,318 168,300 172,282 Z'
    },
    {
      name: 'MADRE DE DIOS',
      path: 'M 205,280 L 220,295 240,300 260,295 280,280 295,260 310,265 318,280 310,300 295,315 275,325 255,328 248,315 240,300 Z'
    },
    {
      name: 'AREQUIPA',
      path: 'M 62,312 L 72,298 78,282 85,305 95,318 108,330 125,335 142,330 148,335 140,355 125,370 108,380 88,382 70,375 55,362 45,345 40,328 Z'
    },
    {
      name: 'PUNO',
      path: 'M 148,335 L 162,345 180,355 200,358 222,350 240,335 248,315 255,328 258,348 250,368 235,385 215,398 192,405 170,400 152,390 140,375 135,358 140,355 Z'
    },
    {
      name: 'MOQUEGUA',
      path: 'M 88,382 L 108,380 125,370 140,375 135,358 140,355 125,370 108,380 105,395 95,405 82,408 72,400 68,390 75,385 Z'
    },
    {
      name: 'TACNA',
      path: 'M 72,400 L 82,408 95,405 105,395 115,402 125,412 120,425 108,435 92,438 78,430 70,418 68,408 Z'
    }
  ];

  // Fix MOQUEGUA path to be more realistic
  departments[23].path = 'M 68,390 L 75,385 88,382 108,380 125,370 140,375 152,390 140,398 122,405 105,405 95,402 82,400 72,398 Z';
  // Fix TACNA
  departments[24].path = 'M 72,398 L 82,400 95,402 105,405 122,405 130,415 122,428 108,435 90,438 76,430 68,418 65,408 Z';

  // Build SVG
  var svgNS = 'http://www.w3.org/2000/svg';

  var svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('viewBox', '15 0 400 460');
  svg.setAttribute('xmlns', svgNS);
  svg.style.width = '100%';
  svg.style.maxWidth = '350px';
  svg.style.height = 'auto';
  svg.style.display = 'block';
  svg.style.margin = '0 auto';

  // Tooltip element
  var tooltip = document.createElement('div');
  tooltip.style.cssText =
    'position:absolute;background:#1e293b;color:#fff;padding:4px 10px;border-radius:4px;' +
    'font-size:12px;font-weight:600;pointer-events:none;opacity:0;transition:opacity 0.15s;' +
    'white-space:nowrap;z-index:1000;transform:translate(-50%,-100%);';
  container.style.position = 'relative';
  container.appendChild(tooltip);

  // Draw each department
  departments.forEach(function (dept) {
    var pathEl = document.createElementNS(svgNS, 'path');
    pathEl.setAttribute('d', dept.path);
    pathEl.setAttribute('data-dept', dept.name);
    pathEl.setAttribute('fill', dept.name === currentDept ? SELECTED_COLOR : DEPT_COLOR);
    pathEl.setAttribute('stroke', dept.name === currentDept ? SELECTED_STROKE : STROKE_COLOR);
    pathEl.setAttribute('stroke-width', dept.name === currentDept ? '2' : '1');
    pathEl.style.cursor = 'pointer';
    pathEl.style.transition = 'fill 0.2s, stroke 0.2s';

    // Hover
    pathEl.addEventListener('mouseenter', function (e) {
      if (dept.name !== currentDept) {
        pathEl.setAttribute('fill', HOVER_COLOR);
      }
      tooltip.textContent = dept.name;
      tooltip.style.opacity = '1';
    });

    pathEl.addEventListener('mousemove', function (e) {
      var rect = container.getBoundingClientRect();
      tooltip.style.left = (e.clientX - rect.left) + 'px';
      tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
    });

    pathEl.addEventListener('mouseleave', function () {
      if (dept.name !== currentDept) {
        pathEl.setAttribute('fill', DEPT_COLOR);
      }
      tooltip.style.opacity = '0';
    });

    // Click: update the department filter select and submit
    pathEl.addEventListener('click', function () {
      var select = document.querySelector('select[name="departamento"]');
      if (select) {
        // Try to find matching option (case-insensitive)
        for (var i = 0; i < select.options.length; i++) {
          if (select.options[i].value.toUpperCase() === dept.name ||
              select.options[i].textContent.toUpperCase().trim() === dept.name) {
            select.selectedIndex = i;
            break;
          }
        }
        // Submit the parent form
        var form = select.closest('form');
        if (form) {
          form.submit();
        }
      } else {
        // Fallback: navigate directly with query parameter
        var url = new URL(window.location.href);
        url.searchParams.set('departamento', dept.name);
        window.location.href = url.toString();
      }
    });

    svg.appendChild(pathEl);
  });

  // Add department labels (small text in center of each region)
  var labelData = [
    { name: 'TUM', x: 62, y: 30 },
    { name: 'PIU', x: 82, y: 72 },
    { name: 'LAM', x: 75, y: 102 },
    { name: 'CAJ', x: 138, y: 100 },
    { name: 'AMA', x: 182, y: 80 },
    { name: 'LOR', x: 290, y: 115 },
    { name: 'SM', x: 172, y: 155 },
    { name: 'LL', x: 92, y: 135 },
    { name: 'ANC', x: 82, y: 165 },
    { name: 'HUA', x: 152, y: 192 },
    { name: 'PAS', x: 118, y: 222 },
    { name: 'UCA', x: 238, y: 245 },
    { name: 'JUN', x: 138, y: 252 },
    { name: 'LIM', x: 58, y: 210 },
    { name: 'CAL', x: 25, y: 200 },
    { name: 'HCV', x: 100, y: 278 },
    { name: 'ICA', x: 48, y: 285 },
    { name: 'AYA', x: 125, y: 308 },
    { name: 'APU', x: 148, y: 292 },
    { name: 'CUS', x: 195, y: 320 },
    { name: 'MDD', x: 272, y: 298 },
    { name: 'ARE', x: 95, y: 355 },
    { name: 'PUN', x: 195, y: 375 },
    { name: 'MOQ', x: 105, y: 395 },
    { name: 'TAC', x: 98, y: 422 }
  ];

  labelData.forEach(function (lbl) {
    var text = document.createElementNS(svgNS, 'text');
    text.setAttribute('x', lbl.x);
    text.setAttribute('y', lbl.y);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dominant-baseline', 'central');
    text.setAttribute('font-size', '7');
    text.setAttribute('font-family', 'Arial, sans-serif');
    text.setAttribute('font-weight', '600');
    text.setAttribute('fill', '#334155');
    text.setAttribute('pointer-events', 'none');
    text.textContent = lbl.name;
    svg.appendChild(text);
  });

  container.appendChild(svg);
}
