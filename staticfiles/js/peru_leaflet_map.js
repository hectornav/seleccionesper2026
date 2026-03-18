/**
 * Peru Interactive Map using Leaflet + OpenStreetMap + GeoJSON departments.
 * Usage: initPeruLeafletMap('container-id')
 */
function initPeruLeafletMap(containerId) {
  var container = document.getElementById(containerId);
  if (!container) return;

  // Current department filter from URL
  var urlParams = new URLSearchParams(window.location.search);
  var currentDept = (urlParams.get('departamento') || '').toUpperCase();

  // Initialize Leaflet map centered on Peru
  var map = L.map(containerId, {
    center: [-9.19, -75.0152],
    zoom: 5,
    minZoom: 4,
    maxZoom: 10,
    zoomControl: true,
    scrollWheelZoom: true,
    attributionControl: true,
  });

  // OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
    maxZoom: 18,
  }).addTo(map);

  // Style functions
  var DEFAULT_STYLE = {
    fillColor: '#dbeafe',
    weight: 1.5,
    color: '#94a3b8',
    fillOpacity: 0.5,
  };

  var HOVER_STYLE = {
    fillColor: '#60a5fa',
    weight: 2,
    color: '#3b82f6',
    fillOpacity: 0.7,
  };

  var SELECTED_STYLE = {
    fillColor: '#3b82f6',
    weight: 3,
    color: '#ffffff',
    fillOpacity: 0.75,
  };

  function getStyle(feature) {
    var name = (feature.properties.NOMBDEP || '').toUpperCase();
    if (name === currentDept) {
      return SELECTED_STYLE;
    }
    return DEFAULT_STYLE;
  }

  // Info control
  var info = L.control({ position: 'topright' });
  info.onAdd = function () {
    this._div = L.DomUtil.create('div', 'leaflet-dept-info');
    this._div.style.cssText =
      'background:rgba(255,255,255,0.95);padding:6px 12px;border-radius:6px;' +
      'font-size:12px;font-weight:700;color:#1e293b;box-shadow:0 1px 4px rgba(0,0,0,0.15);' +
      'pointer-events:none;min-width:80px;text-align:center;display:none;';
    return this._div;
  };
  info.update = function (name) {
    if (name) {
      this._div.style.display = 'block';
      this._div.innerHTML = name;
    } else {
      this._div.style.display = 'none';
    }
  };
  info.addTo(map);

  var geojsonLayer;

  // Load GeoJSON
  var geojsonUrl = container.getAttribute('data-geojson') || '/static/data/peru_departamentos.geojson';

  fetch(geojsonUrl)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      geojsonLayer = L.geoJSON(data, {
        style: getStyle,
        onEachFeature: function (feature, layer) {
          var deptName = (feature.properties.NOMBDEP || '').toUpperCase();

          layer.on('mouseover', function (e) {
            if (deptName !== currentDept) {
              layer.setStyle(HOVER_STYLE);
            }
            info.update(deptName);
            layer.bringToFront();
          });

          layer.on('mouseout', function () {
            if (deptName !== currentDept) {
              layer.setStyle(DEFAULT_STYLE);
            }
            info.update(null);
          });

          layer.on('click', function () {
            // Update the department select and submit form
            var select = document.querySelector('select[name="departamento"]');
            if (select) {
              var found = false;
              for (var i = 0; i < select.options.length; i++) {
                if (select.options[i].value.toUpperCase() === deptName ||
                    select.options[i].textContent.toUpperCase().trim() === deptName) {
                  select.selectedIndex = i;
                  found = true;
                  break;
                }
              }
              if (found) {
                var form = select.closest('form');
                if (form) form.submit();
              }
            } else {
              // Fallback: navigate directly
              var url = new URL(window.location.href);
              url.searchParams.set('departamento', deptName);
              window.location.href = url.toString();
            }
          });
        },
      }).addTo(map);

      // Fit bounds to Peru
      map.fitBounds(geojsonLayer.getBounds(), { padding: [10, 10] });
    })
    .catch(function (err) {
      console.error('Error loading Peru GeoJSON:', err);
    });
}
