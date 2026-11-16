(() => {
  'use strict';
  const dialog = document.querySelector('#atlas-map-dialog');
  if (!dialog) return;
  const frameBox = document.querySelector('#atlas-live-frame');
  const status = document.querySelector('#atlas-map-status');
  let slowTimer;
  function activate(section, location) {
    section.querySelectorAll('[data-atlas-pin]').forEach(pin => {
      pin.setAttribute('aria-pressed', String(pin.dataset.atlasPin === location));
    });
  }
  for (const section of document.querySelectorAll('.atlas-section')) {
    const pins = [...section.querySelectorAll('[data-atlas-pin]')];
    const details = [...section.querySelectorAll('details[data-location]')];
    for (const pin of pins) {
      const select = () => {
        const target = details.find(d => d.dataset.location === pin.dataset.atlasPin);
        if (!target) return;
        details.forEach(d => { d.open = d === target; });
        activate(section, target.dataset.location);
        target.querySelector('summary').focus({preventScroll:true});
        if (target.getBoundingClientRect().top > innerHeight - 80) target.scrollIntoView({block:'nearest'});
      };
      pin.addEventListener('click', select);
      pin.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(); }
      });
    }
    for (const detail of details) detail.addEventListener('toggle', () => {
      if (detail.open) activate(section, detail.dataset.location);
    });
  }
  document.querySelector('main').addEventListener('click', e => {
    const button = e.target.closest('[data-map-open]');
    if (!button) return;
    const place = button.closest('[data-location]');
    const lat = Number(place.dataset.lat), lon = Number(place.dataset.lon);
    const name = place.querySelector('summary span:nth-child(2)').firstChild.textContent.trim();
    const params = new URLSearchParams({bbox:[lon-.08,lat-.05,lon+.08,lat+.05].join(','),layer:'mapnik',marker:`${lat},${lon}`});
    const frame = document.createElement('iframe');
    frame.title = name + ' · OpenStreetMap 现代地图';
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    document.querySelector('#atlas-online-title').textContent = name + ' · 在线地图';
    document.querySelector('#atlas-live-links').replaceChildren(...[...place.querySelectorAll('.atlas-links a')].map(a => a.cloneNode(true)));
    frameBox.replaceChildren(frame);
    status.textContent = '正在联系 OpenStreetMap。也可直接打开下面的地图源。';
    clearTimeout(slowTimer);
    slowTimer = setTimeout(() => {
      status.textContent = '若图层仍未出现，可改用 Google Maps 或 Bing Maps，或返回教学图。';
    }, 6500);
    frame.addEventListener('load', () => {
      // Cross-origin tile availability cannot be inferred from iframe load.
      if (dialog.open) status.textContent = '若图层未出现，可改用其他地图源。';
    });
    dialog.showModal();
    frame.src = 'https://www.openstreetmap.org/export/embed.html?' + params;
  });
  dialog.addEventListener('close', () => {
    clearTimeout(slowTimer);
    frameBox.replaceChildren();
  });
})();
