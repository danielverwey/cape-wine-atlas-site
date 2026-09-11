
(async function(){

  /* ---- assets & data ----
     In the published site everything is fetched relative to ROOT; the archival
     single-file build sets window.__CWA with the same things inlined. */
  const INLINE = window.__CWA || {};
  const ROOT = (document.documentElement.dataset.root || '/');
  const asset = p => INLINE.assets && INLINE.assets[p] ? INLINE.assets[p] : ROOT + 'assets/' + p;
  const FOOTER_HALFTONE_SRC = asset('img/footer-halftone.jpg');
  const MAP_TEX_SRC = asset('img/map-tex.jpg');
  const HERO_TEX_SRC = asset('img/hero-tex.jpg');
  const ATLAS = INLINE.index || await (await fetch(ROOT + 'data/index.json', { cache: 'no-cache' })).json();
  const GEO = ATLAS.geo, MAP_MARKS = ATLAS.marks;
  const regionCache = INLINE.regions || {};
  async function loadRegion(key){
    if(regionCache[key]) return regionCache[key];
    const r = await fetch(ROOT + 'data/regions/' + key + '.json', { cache: 'no-cache' });
    if(!r.ok) throw new Error('region not found: ' + key);
    return (regionCache[key] = await r.json());
  }
  const BOOT_REGION = document.documentElement.dataset.region || '';
  // the archival single file is opened from disk, where the history API refuses new addresses
  const canRoute = /^https?:$/.test(location.protocol);
  const push = (state, url) => { if(canRoute){ try { history.pushState(state, '', url); } catch(e){} } };
  const EDITION = (() => { const d = new Date(ATLAS.stats.built); return isNaN(d) ? 'CURRENT EDITION' : d.toLocaleString('en-GB', { month:'long', year:'numeric' }).toUpperCase() + ' EDITION'; })();

  /* =========================================================
     1. PRELOADER
     ========================================================= */
  const ST = ATLAS.stats;
  const compShort = { 'Critic reviews':'CRITICS', 'London Wine Competition':'LONDON', "Platter's":'PLATTER’S', 'Trophy Wine Show':'TROPHY WINE SHOW' };
  const compList = (ST.competitions || []).map(c => (compShort[c.body] || c.body).toUpperCase()).join(' · ');
  const ld = n => `<i class="ld">${'.'.repeat(n)}</i>`;   // dotted leader — hidden on phones, where each result takes its own line
  const logLines = [
    `&gt;&gt; LINKING CAPE WINE ATLAS ${ld(12)} <span class='g'>DONE</span>`,
    `&gt;&gt; OPENING THE ATLAS RECORD ${ld(11)} <span class='g'>${ST.farms} FARMS · ${ST.regions} REGIONS</span>`,
    `&gt;&gt; WINE ROUTES ${ld(25)} <span class='g'>${ST.routes} ON FILE</span>`,
    `&gt;&gt; TOUR OPERATORS ${ld(22)} <span class='g'>${ST.tours} LISTED</span>`,
    `&gt;&gt; HONOURS LEDGER ${ld(22)} <span class='g'>${ST.verifiedAwards} VERIFIED · ${ST.pendingClaims} UNDER REVIEW</span>`,
    `&gt;&gt; COMPETITIONS CONSULTED ${ld(14)} <span class='g'>${compList}</span>`,
    `&gt;&gt; PROVENANCE CHECK ${ld(20)} <span class='g'>EVERY ENTRY TRACEABLE TO ITS SOURCE</span>`,
    `&gt;&gt; ATLAS READY ${ld(25)} <span class='g'>OPEN</span>`
  ];
  const plLog = document.getElementById('plLog');
  const plPct = document.getElementById('plPct');
  const plBar = document.getElementById('plBar');
  const enterBtn = document.getElementById('enterBtn');
  logLines.forEach(()=>{ const d=document.createElement('div'); plLog.appendChild(d); });

  let pct = 0;
  const plInterval = setInterval(()=>{
    pct += Math.random()*9 + 4;
    if(pct >= 100){ pct = 100; clearInterval(plInterval); enterBtn.classList.add('ready'); enterBtn.focus({ preventScroll: true }); document.getElementById('plGeo').classList.add('show'); }
    plPct.textContent = 'LOADING ' + Math.floor(pct) + ' / 100';
    plBar.style.width = pct + '%';
    const shown = Math.min(logLines.length, Math.ceil((pct/100)*logLines.length));
    Array.from(plLog.children).forEach((el,i)=>{
      if(i < shown){ el.classList.add('show'); el.innerHTML = logLines[i]; }
    });
  }, 220);

  enterBtn.addEventListener('click', () => {
    document.getElementById('preloader').classList.add('hide');
    document.getElementById('chrome').classList.add('show');
    startParticles();
  });

  /* =========================================================
     2. SOUND / MENU TOGGLES (cosmetic)
     ========================================================= */

  /* =========================================================
     3. TYPEWRITER HELPER
     ========================================================= */
  function typewrite(el, text, speed){
    el.innerHTML = '';
    let i = 0;
    const cursor = document.createElement('span');
    cursor.className = 'cursor'; cursor.textContent = '|';
    function step(){
      el.textContent = text.slice(0, i);
      el.appendChild(cursor);
      i++;
      if(i <= text.length){ setTimeout(step, speed); }
    }
    step();
  }

  const heroCaptionText = "A living atlas of South Africa’s wine farms — every estate a single record of its route, its whereabouts, its opening hours, the grapes it grows and the honours it has earned. Nothing is written here without a source, and where the research has not yet reached, the atlas says so plainly.";
  // numbers in words, so the title card reads like a book rather than a ledger
  function words(n){
    const ones = ['','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen'];
    const tens = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety'];
    if(n < 20) return ones[n];
    if(n < 100) return tens[Math.floor(n/10)] + (n%10 ? '-' + ones[n%10] : '');
    if(n < 1000){ const h = Math.floor(n/100), r = n % 100; return ones[h] + ' hundred' + (r ? ' and ' + words(r) : ''); }
    const th = Math.floor(n/1000), r = n % 1000;
    if(th < 10 && r >= 100) return words(th*10 + Math.floor(r/100)) + ' hundred' + (r%100 ? ' and ' + words(r%100) : '');   // "eleven hundred and thirty-three"
    return words(th) + ' thousand' + (r ? (r < 100 ? ' and ' : ' ') + words(r) : '');
  }
  const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
  const cellars = ATLAS.stats.industry && ATLAS.stats.industry.cellars;
  const tcText = `${cap(words(ST.regions))} regions, gathered one farm at a time — from the old valley of Constantia to the shores of Plettenberg Bay, from Nieuwoudtville to Cape Agulhas. ${cap(words(ST.farms))} producers stand on record${cellars ? `, against the ${words(cellars)} cellars the industry itself counted crushing grapes in 2024` : ''}; ${words(ST.verifiedAwards)} honours are verified against their sources, and every claim still awaiting confirmation is marked as such.`;

  setTimeout(()=> typewrite(document.getElementById('heroCaption'), heroCaptionText, 22), 1200);

  /* =========================================================
     4. SECTION REVEAL (IntersectionObserver)
     ========================================================= */
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add('visible');
        if(entry.target.id === 'tcInner'){ typewrite(document.getElementById('tcText'), tcText, 18); }
        if(entry.target.id === 'termWindow'){ /* already CSS-revealed */ }
        io.unobserve(entry.target);
      }
    });
  }, { threshold:0.35 });
  document.querySelectorAll('.reveal, #termWindow').forEach(el=> io.observe(el));

  // footer: HUD frame draws on, then button / links / bottom row stagger in (reference: GSAP timeline at 30% visibility)
  const footerEl = document.getElementById('footer');
  new IntersectionObserver((entries, obs)=>{
    entries.forEach(e=>{ if(e.isIntersecting){ footerEl.classList.add('visible'); obs.unobserve(e.target); } });
  }, { threshold: 0.3 }).observe(footerEl);

  /* ---- footer "hidden halftone" pixel reveal (reference: 80×40 pixel grid; cells light up
          around the cursor where a hidden image is dark, with a little glitch jitter) ---- */
  (function(){
    const cv = document.getElementById('footerPix');
    const fx = cv.getContext('2d');
    const COLS = 80, ROWS = 40, R = 16;
    let pattern = null, mx = -1, my = -1, cw = 0, chh = 0, lastMove = 0;
    const himg = new Image();
    himg.onload = () => {
      const c = document.createElement('canvas'); c.width = COLS; c.height = ROWS;
      const x = c.getContext('2d'); x.drawImage(himg, 0, 0, COLS, ROWS);
      const d = x.getImageData(0, 0, COLS, ROWS).data;
      pattern = new Float32Array(COLS * ROWS);
      for(let i = 0, p = 0; i < d.length; i += 4, p++) pattern[p] = 1 - (0.299*d[i] + 0.587*d[i+1] + 0.114*d[i+2]) / 255;
    };
    himg.src = FOOTER_HALFTONE_SRC;
    function size(){
      const r = cv.getBoundingClientRect();
      cv.width = Math.round(r.width); cv.height = Math.round(r.height);
      cw = cv.width / COLS; chh = cv.height / ROWS;
    }
    size(); window.addEventListener('resize', size);
    const pops = [];
    // the text that the reveal can run over: while the darkened cells cover it, it switches to a pale tone so it stays legible
    const litEls = [...footerEl.querySelectorAll('.f-h, .f-mail, .f-stamp, .f-mid p, .f-line span, .f-bottom .l, .f-bottom .r, .f-bottom .c .display')];
    let litTick = 0;
    function relight(active){
      const r = cv.getBoundingClientRect();
      const cx = r.left + mx * r.width, cy = r.top + my * r.height, rx = R * cw * 0.9, ry = R * chh * 0.9;
      for(const el of litEls){
        let on = false;
        if(active){
          const b = el.getBoundingClientRect();
          const nx = Math.max(b.left, Math.min(cx, b.right)), ny = Math.max(b.top, Math.min(cy, b.bottom));   // nearest point of the box to the cursor
          on = ((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2 <= 1;
        }
        el.classList.toggle('lit', on);
      }
    }
    function draw(){
      fx.clearRect(0, 0, cv.width, cv.height);
      if(!pattern) return;
      const t = performance.now();
      const fade = Math.max(0, 1 - (t - lastMove) / 900);        // trail lingers ~1s after the cursor stops
      if(++litTick % 3 === 0) relight(mx >= 0 && fade > 0.15);
      if(mx >= 0 && fade > 0){
        const col = Math.floor(mx * COLS), row = Math.floor(my * ROWS);
        for(let r = Math.max(0, row - R); r <= Math.min(ROWS - 1, row + R); r++){
          for(let c = Math.max(0, col - R); c <= Math.min(COLS - 1, col + R); c++){
            const v = pattern[r * COLS + c];
            const dist = Math.hypot(r - row, c - col) + Math.random() * 0.8;
            let a = 0;
            if(v > 0.7){ a = dist <= 8 ? 1 : dist <= 12 ? 0.8 : dist <= 16 ? 0.6 : 0; }
            else if(v > 0.5){ a = dist <= 6 ? 0.8 : dist <= 10 ? 0.6 : 0; }
            else if(v > 0.3 && dist <= 6){ a = 0.6; }
            if(!a) continue;
            const jx = Math.random() < 0.1 ? (Math.random() - 0.5) * 6 : 0;
            fx.fillStyle = `rgba(150,118,0,${(a * fade).toFixed(2)})`;
            fx.fillRect(c * cw + jx + 1, r * chh + 1, cw - 2, chh - 2);
          }
        }
      }
      // random single-cell pops (reference: one every 2s, 0.6s life)
      for(let i = pops.length - 1; i >= 0; i--){
        const p = pops[i], k = (t - p.t) / 600;
        if(k >= 1){ pops.splice(i, 1); continue; }
        fx.fillStyle = `rgba(150,118,0,${(Math.sin(k * Math.PI) * 0.9).toFixed(2)})`;
        fx.fillRect(p.c * cw + 1, p.r * chh + 1, cw - 2, chh - 2);
      }
    }
    setInterval(()=>{ pops.push({ c: Math.floor(Math.random()*COLS), r: Math.floor(Math.random()*ROWS), t: performance.now() }); }, 2000);
    footerEl.addEventListener('mousemove', e=>{
      const r = cv.getBoundingClientRect();
      mx = (e.clientX - r.left) / r.width; my = (e.clientY - r.top) / r.height; lastMove = performance.now();
    }, { passive:true });
    footerEl.addEventListener('mouseenter', ()=>{ for(let i=0;i<5;i++) setTimeout(()=>pops.push({ c: Math.floor(Math.random()*COLS), r: Math.floor(Math.random()*ROWS), t: performance.now() }), i*100); });
    footerEl.addEventListener('mouseleave', ()=>{ mx = -1; });
    (function loop(){ draw(); requestAnimationFrame(loop); })();
  })();

  /* =========================================================
     5. MOTIF CLUSTERS — clean radar/HUD geometry (concentric
        rings, crosshair ticks, small blips), matching the
        reference site rather than illustrative icons.
        Rotation is driven by SCROLL POSITION (not time).
     ========================================================= */
  // hairline HUD rings — the same weight as the preloader geometry (0.5px strokes, ~15% white),
  // not a heavy instrument dial. A few fine ticks and 4 marker dots, nothing more.
  function buildCluster(el, tickCount, blipCount){
    const R1 = 47, R2 = 36, R3 = 22;
    let ticks = '';
    for(let i=0;i<tickCount;i++){
      const a = (i / tickCount) * Math.PI * 2;
      const cos = Math.cos(a), sin = Math.sin(a);
      const isCardinal = i % (tickCount/4 || 1) === 0;
      const len = isCardinal ? 2.4 : 1.1;
      ticks += `<line class="motif-tick" x1="${(50+R1*cos).toFixed(2)}" y1="${(50+R1*sin).toFixed(2)}" x2="${(50+(R1+len)*cos).toFixed(2)}" y2="${(50+(R1+len)*sin).toFixed(2)}"/>`;
    }
    let blips = '';
    for(let i=0;i<blipCount;i++){
      const a = (i / blipCount) * Math.PI * 2 + 0.4;
      blips += `<circle cx="${(50+R2*Math.cos(a)).toFixed(2)}" cy="${(50+R2*Math.sin(a)).toFixed(2)}" r="0.32" style="fill:${i===0?'var(--gold)':'rgba(234,234,234,0.55)'};stroke:none"/>`;
    }
    el.innerHTML = `<svg viewBox="0 0 100 100">
      <circle class="motif-ring-line" cx="50" cy="50" r="${R1}"/>
      <circle class="motif-ring-line" cx="50" cy="50" r="${R2}" stroke-dasharray="0.6 1.6"/>
      <circle class="motif-ring-line" cx="50" cy="50" r="${R3}"/>
      <circle class="motif-ring-line" cx="50" cy="50" r="6"/>
      <line class="motif-cross" x1="50" y1="2" x2="50" y2="98"/>
      <line class="motif-cross" x1="2" y1="50" x2="98" y2="50"/>
      ${ticks}
      ${blips}
    </svg>`;
  }
  const c1 = document.getElementById('cluster1');
  const c2 = document.getElementById('cluster2');
  const c3 = document.getElementById('cluster3');
  buildCluster(c1, 12, 5);
  buildCluster(c2, 8, 3);
  buildCluster(c3, 16, 7);

  // independent rate + direction per cluster, proportional to scrollY (scrubbed, not time-based)
  const clusters = [
    { el:c1, rate: 0.09,  dir: 1 },
    { el:c2, rate: 0.16,  dir: -1 },
    { el:c3, rate: 0.03, dir: 1 }
  ];
  function updateRotation(){
    const y = window.scrollY;
    clusters.forEach(c=>{
      const deg = y * c.rate * c.dir;
      const base = c.el.id === 'cluster3' ? 'translate(-50%,-50%) ' : '';
      c.el.style.transform = base + `rotate(${deg}deg)`;
    });
  }
  window.addEventListener('scroll', ()=> requestAnimationFrame(updateRotation), { passive:true });
  updateRotation();

  /* =========================================================
     6. HERO — "POINT-CLOUD DOT-SCREEN" (reference-accurate)
        Verified against the reference's actual renderer (a Three.js
        points grid, 162 rows × N columns, one point per cell):
        · each point is a soft disc, textured with ITS CELL of a
          pre-stylised black/white "point-cloud" image (black sky &
          ground, white edge-lines & highlights). Dark fragments are
          discarded — so the render is literally
              stylised texture × dot-screen mask.
          The photo is legible because the TEXTURE is legible; the
          dots just add the halftone/noise feel.
        · breathing: the whole plane moves toward/away from the
          camera by ±10 units (camera at 250) on a ~4.2 s sine —
          a ±4 % zoom in/out of the entire picture, dots included.
        · entry: every point starts at a random depth in front of
          the plane and flies in over 2.5 s (Power4 ease-out) while
          fading up.
        · a bloom pass makes the bright dots glow.
        · fast mouse moves leave a trail that pushes nearby points
          toward the camera (a soft lens bulge that decays in ~1 s).
        Implemented in Canvas 2D: the masked texture is baked ONCE
        into an offscreen layer (plus a blurred bloom copy); each
        frame just draws those layers under a scale transform, so
        the steady state costs 2–3 full-screen blits, not 40k draws.
     ========================================================= */
  const canvas = document.getElementById('particleCanvas');
  const ctx = canvas.getContext('2d');
  let W = 0, H = 0, DPR = 1;

  const CAM_Z = 250;          // camera distance to the point plane (world units)
  const GRID_ROWS = 162;      // reference: 9 × 18 rows
  const DOT_D = 0.76;         // disc diameter as a fraction of the cell pitch
  const OVERSCAN = 1.10;      // bake the layer slightly larger than the viewport so zoom-out never shows edges
  const REDUCED_MOTION = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const BREATH_AMP = REDUCED_MOTION ? 0 : 10;      // ±10 world units toward/away from camera; still when the reader asks for less motion
  const BREATH_SPEED = 1.5;   // rad/s  → period ≈ 4.2 s
  const ENTRY_MS = 2500;
  const BLOOM_ALPHA = 0.55;

  let layer = null, bloom = null, lens = null, lensMask = null;
  let LW = 0, LH = 0;                 // layer size (css px)
  let grid = null;                    // { nx, ny, pitch, ox, oy, lit:Int32Array (cell indices), z0:Float32Array }
  let texReady = false;
  const tex = new Image();
  tex.onload = () => { texReady = true; if (W && H) bake(); };
  tex.src = HERO_TEX_SRC;

  function resize(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = Math.round(W * DPR); canvas.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    if (texReady) bake();
  }

  // ---------- WebKit-safe filtering ----------
  // Safari (every iPhone and iPad, and Mac Safari) does not expose CanvasRenderingContext2D.filter, so the
  // brightness/contrast and bloom-blur passes below take a pixel path there: a LUT for tone, and a
  // successive-halving downscale + smooth upscale for the blur. Same look, one-time cost at bake.
  const HAS_FILTER = (() => { try { return typeof document.createElement('canvas').getContext('2d').filter === 'string'; } catch(e){ return false; } })();
  function tone(cnv, brightness, contrast){
    if (brightness === 1 && contrast === 1) return cnv;
    const c = cnv.getContext('2d'), img = c.getImageData(0, 0, cnv.width, cnv.height), d = img.data;
    const lut = new Uint8ClampedArray(256);
    for (let i = 0; i < 256; i++) lut[i] = (i * brightness - 128) * contrast + 128;
    for (let i = 0; i < d.length; i += 4){ d[i] = lut[d[i]]; d[i+1] = lut[d[i+1]]; d[i+2] = lut[d[i+2]]; }
    c.putImageData(img, 0, 0);
    return cnv;
  }
  function blurred(src, radius, outW, outH){
    // halve until the image is about `radius` times smaller (each halving box-averages 2×2), then upscale smoothly
    let cur = src, w = src.width, h = src.height;
    const target = Math.max(1, Math.round(w / Math.max(2, radius * 2)));   // a Gaussian of σ=r spreads about 2r
    while (w / 2 >= target){
      const nw = Math.max(1, Math.round(w / 2)), nh = Math.max(1, Math.round(h / 2));
      const c = document.createElement('canvas'); c.width = nw; c.height = nh;
      const cc = c.getContext('2d'); cc.imageSmoothingEnabled = true; cc.imageSmoothingQuality = 'high';
      cc.drawImage(cur, 0, 0, nw, nh);
      cur = c; w = nw; h = nh;
    }
    const mid = document.createElement('canvas'); mid.width = Math.max(1, w * 2); mid.height = Math.max(1, h * 2);
    const mc = mid.getContext('2d'); mc.imageSmoothingEnabled = true; mc.imageSmoothingQuality = 'high';
    mc.drawImage(cur, 0, 0, mid.width, mid.height);
    const out = document.createElement('canvas'); out.width = outW; out.height = outH;
    const oc = out.getContext('2d'); oc.imageSmoothingEnabled = true; oc.imageSmoothingQuality = 'high';
    oc.drawImage(mid, 0, 0, outW, outH);
    return out;
  }
  // draw `src` into ctx with a filter string, or the pixel-path equivalent: {brightness, contrast, blur}
  function drawFiltered(ctx, src, f, dx, dy, dw, dh){
    dw = dw === undefined ? src.width : dw; dh = dh === undefined ? src.height : dh;
    if (HAS_FILTER){
      ctx.filter = (f.contrast && f.contrast !== 1 ? `contrast(${f.contrast}) ` : '') + (f.brightness && f.brightness !== 1 ? `brightness(${f.brightness}) ` : '') + (f.blur ? `blur(${f.blur}px)` : '') || 'none';
      ctx.drawImage(src, dx, dy, dw, dh);
      ctx.filter = 'none';
      return;
    }
    let img = src;
    if (f.blur){
      img = blurred(src, f.blur, Math.max(1, Math.round(src.width / 2)), Math.max(1, Math.round(src.height / 2)));
      tone(img, f.brightness || 1, f.contrast || 1);
    } else if ((f.brightness && f.brightness !== 1) || (f.contrast && f.contrast !== 1)){
      const t = ctx.getTransform();   // size the tone buffer at device pixels so nothing is resampled twice
      const c = document.createElement('canvas'); c.width = Math.max(1, Math.round(dw * (t.a || 1))); c.height = Math.max(1, Math.round(dh * (t.d || 1)));
      const cc = c.getContext('2d'); cc.imageSmoothingEnabled = true; cc.imageSmoothingQuality = 'high';
      cc.drawImage(src, 0, 0, c.width, c.height);
      tone(c, f.brightness || 1, f.contrast || 1);
      img = c;
    }
    ctx.drawImage(img, dx, dy, dw, dh);
  }

  // The charts used a fixed 150-row grid, so on a phone or a 13-inch laptop the dots shrank to a grain
  // and the coastline, ridges and roads — thin lines in the source — fell between them. The grid now
  // keeps its dots at least ~4 px across (fewer rows on a small canvas), and where the dots are small
  // the source is spread and brightened a little so a thin line still fills its dot.
  function gridRows(ch, minPitch){ return Math.max(56, Math.min(150, Math.round(ch / (minPitch || 4.2)))); }
  function fineBlur(pitch){ return pitch < 5.5 ? +(pitch * 0.32).toFixed(2) : 0; }
  function fineBoost(pitch){ return pitch < 5.5 ? 1 + (5.5 - pitch) * 0.12 : 1; }

  function makeDisc(dPx){
    // soft-edged disc sprite, like the shader's circle(): solid core, short alpha ramp at the rim, faint rim highlight
    const s = document.createElement('canvas');
    const dim = Math.max(2, Math.ceil(dPx) + 2);
    s.width = dim; s.height = dim;
    const c = s.getContext('2d');
    const r = dPx / 2;
    const g = c.createRadialGradient(dim/2, dim/2, 0, dim/2, dim/2, r);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.62, 'rgba(255,255,255,1)');
    g.addColorStop(0.80, 'rgba(255,255,255,0.9)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    c.fillStyle = g;
    c.beginPath(); c.arc(dim/2, dim/2, r, 0, Math.PI*2); c.fill();
    return s;
  }

  function bake(){
    LW = Math.ceil(W * OVERSCAN); LH = Math.ceil(H * OVERSCAN);
    const aspect = tex.width / tex.height;
    // reference: the 162-row grid spans ~89% of the visible height; on wide screens the picture
    // sits inside the frame (its edges are black anyway). A phone held upright would crop it to a
    // third, so there the picture is fitted a little wider than the screen instead — stadium and
    // mountain both kept — with fewer, never finer, dots so the screen still reads as dots.
    let ny, nx, pitch;
    if (H > W * 1.05){
      const gwT = W * 1.4, ghT = gwT / aspect;
      pitch = Math.max(3.2, ghT / GRID_ROWS);
      ny = Math.round(ghT / pitch); nx = Math.round(ny * aspect);
    } else {
      ny = GRID_ROWS; nx = Math.round(ny * aspect);
      pitch = (H * 0.98) / ny;
    }
    const gw = nx * pitch, gh = ny * pitch;
    const ox = (LW - gw) / 2, oy = (LH - gh) / 2;

    // --- 1. per-cell brightness (area-averaged) → which cells are lit at all + entry depths
    const sc = document.createElement('canvas'); sc.width = nx; sc.height = ny;
    const sctx = sc.getContext('2d');
    sctx.drawImage(tex, 0, 0, nx, ny);
    const id = sctx.getImageData(0, 0, nx, ny).data;
    const litList = [];
    const cellAlpha = new Float32Array(nx * ny);
    for (let i = 0, p = 0; i < id.length; i += 4, p++){
      const b = id[i] / 255;
      // static per-cell grain: random dimming + a little dropout, like the texel-aliasing in the reference
      const r = Math.random();
      let a = b < 0.06 ? 0 : (r < 0.08 ? 0 : 0.7 + 0.3 * Math.random());
      cellAlpha[p] = a;
      if (a > 0) litList.push(p);
    }
    const lit = Int32Array.from(litList);
    const z0 = new Float32Array(lit.length);
    for (let i = 0; i < z0.length; i++) z0[i] = Math.random() * 500;   // initPosition.z ∈ [0,500)
    grid = { nx, ny, pitch, ox, oy, lit, z0, cellAlpha };

    // --- 2. dot-screen mask (one soft disc per cell, per-cell alpha)
    const mask = document.createElement('canvas');
    mask.width = Math.round(LW * DPR); mask.height = Math.round(LH * DPR);
    const mctx = mask.getContext('2d');
    mctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    const dPx = pitch * DOT_D;
    const disc = makeDisc(dPx * DPR);
    const dd = disc.width / DPR;
    for (let k = 0; k < lit.length; k++){
      const p = lit[k];
      const cx = ox + ((p % nx) + 0.5) * pitch, cy = oy + (Math.floor(p / nx) + 0.5) * pitch;
      mctx.globalAlpha = cellAlpha[p];
      mctx.drawImage(disc, cx - dd/2, cy - dd/2, dd, dd);
    }
    mctx.globalAlpha = 1;

    // --- 3. layer = texture × mask
    layer = document.createElement('canvas');
    layer.width = mask.width; layer.height = mask.height;
    const lctx = layer.getContext('2d');
    lctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    lctx.imageSmoothingEnabled = true;
    drawFiltered(lctx, tex, { brightness: 1.2, contrast: 1.12 }, ox, oy, gw, gh);
    lctx.setTransform(1, 0, 0, 1, 0, 0);
    lctx.globalCompositeOperation = 'destination-in';
    lctx.drawImage(mask, 0, 0);
    lctx.globalCompositeOperation = 'source-over';

    // --- 4. bloom = thresholded, blurred copy (one-time filter cost)
    bloom = document.createElement('canvas');
    bloom.width = Math.round(layer.width / 2); bloom.height = Math.round(layer.height / 2);
    const bctx = bloom.getContext('2d');
    drawFiltered(bctx, layer, { contrast: 1.6, brightness: 0.9, blur: Math.max(2, pitch * 0.9 * DPR / 2) }, 0, 0, bloom.width, bloom.height);

    // --- 5. lens buffers for the hover bulge
    lens = document.createElement('canvas'); lens.width = canvas.width; lens.height = canvas.height;
    lensMask = document.createElement('canvas'); lensMask.width = 96; lensMask.height = Math.round(96 * H / W);
  }

  // ---------- breathing + projection helpers ----------
  function breathZ(nowMs){ return BREATH_AMP * Math.sin(nowMs / 1000 * BREATH_SPEED); }
  function scaleForZ(z){ return CAM_Z / (CAM_Z - z); }          // perspective: nearer → bigger & pushed outward

  function drawLayers(scale, alpha){
    // draws the baked layer (+ bloom) scaled about the viewport centre
    const s = scale;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(W / 2, H / 2); ctx.scale(s, s); ctx.translate(-LW / 2, -LH / 2);
    ctx.drawImage(layer, 0, 0, LW, LH);
    ctx.globalCompositeOperation = 'lighter';
    ctx.globalAlpha = alpha * BLOOM_ALPHA;
    ctx.drawImage(bloom, 0, 0, LW, LH);
    ctx.restore();
  }

  // ---------- hover "touch" trail (reference: 64px touch texture, radius .15, maxAge 60 frames) ----------
  const trail = [];
  const TRAIL_MAX_AGE = 60, TRAIL_RADIUS = 0.15;
  let lastTouch = null;
  function easeOutSine(t){ return Math.sin(t * Math.PI / 2); }
  function addTouch(nx, ny){
    let force = 0;
    if (lastTouch){ const dx = lastTouch.x - nx, dy = lastTouch.y - ny; force = Math.min((dx*dx + dy*dy) * 1e4, 1); }
    lastTouch = { x: nx, y: ny };
    if (force > 0.02) trail.push({ x: nx, y: ny, age: 0, force });
    if (trail.length > 40) trail.shift();
  }
  const heroEl = document.getElementById('hero');
  heroEl.addEventListener('mousemove', e => {
    const r = canvas.getBoundingClientRect();
    addTouch((e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height);
  }, { passive: true });
  heroEl.addEventListener('mouseleave', () => { lastTouch = null; });

  function drawLens(baseScale, alpha){
    if (!trail.length) return;
    // age + cull
    for (let i = trail.length - 1; i >= 0; i--){ if (++trail[i].age > TRAIL_MAX_AGE) trail.splice(i, 1); }
    if (!trail.length) return;
    // mask: soft radial blobs, ramp in over 30 % of life then fade out (same envelope as the reference)
    const mk = lensMask.getContext('2d');
    mk.clearRect(0, 0, lensMask.width, lensMask.height);
    for (const t of trail){
      let n = t.age < TRAIL_MAX_AGE * 0.3 ? easeOutSine(t.age / (TRAIL_MAX_AGE * 0.3)) : easeOutSine(1 - (t.age - TRAIL_MAX_AGE * 0.3) / (TRAIL_MAX_AGE * 0.7));
      n *= t.force;
      const rad = lensMask.width * TRAIL_RADIUS * n;
      if (rad < 0.5) continue;
      const cx = t.x * lensMask.width, cy = t.y * lensMask.height;
      const g = mk.createRadialGradient(cx, cy, rad * 0.25, cx, cy, rad);
      g.addColorStop(0, 'rgba(255,255,255,0.9)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      mk.fillStyle = g; mk.beginPath(); mk.arc(cx, cy, rad, 0, Math.PI * 2); mk.fill();
    }
    // lens = layer drawn slightly nearer the camera (z += 14 → ~6 % bigger, pushed outward), through the mask
    const lc = lens.getContext('2d');
    lc.setTransform(1, 0, 0, 1, 0, 0);
    lc.clearRect(0, 0, lens.width, lens.height);
    lc.setTransform(DPR, 0, 0, DPR, 0, 0);
    const s = baseScale * scaleForZ(14);
    lc.translate(W / 2, H / 2); lc.scale(s, s); lc.translate(-LW / 2, -LH / 2);
    lc.drawImage(layer, 0, 0, LW, LH);
    lc.globalCompositeOperation = 'lighter'; lc.globalAlpha = BLOOM_ALPHA;
    lc.drawImage(bloom, 0, 0, LW, LH);
    lc.setTransform(1, 0, 0, 1, 0, 0);
    lc.globalAlpha = 1;
    lc.globalCompositeOperation = 'destination-in';
    lc.imageSmoothingEnabled = true;
    lc.drawImage(lensMask, 0, 0, lens.width, lens.height);
    lc.globalCompositeOperation = 'source-over';
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = alpha;
    ctx.drawImage(lens, 0, 0);
    ctx.restore();
  }

  // ---------- entry: points fly in from random depth ----------
  function easeOutPow4(t){ return 1 - Math.pow(1 - t, 4); }
  let entryStart = 0, running = false;

  function drawEntry(progress, zb){
    // per-cell draw: each lit cell's patch of the baked layer, projected from its own depth
    const { nx, pitch, ox, oy, lit, z0 } = grid;
    const offX = (W - LW) / 2, offY = (H - LH) / 2;    // layer → screen
    const cxS = W / 2, cyS = H / 2;
    const sLayer = layer, px = pitch * DPR;
    ctx.save();
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = progress;
    for (let k = 0; k < lit.length; k++){
      const z = z0[k] * (1 - progress) + zb;
      if (z > CAM_Z - 12) continue;                       // behind / at the camera: not visible
      const p = lit[k];
      const col = p % nx, row = (p / nx) | 0;
      const lx = ox + col * pitch, ly = oy + row * pitch; // cell top-left in layer css px
      const sx = lx + offX, sy = ly + offY;               // steady-state screen position
      const sc = scaleForZ(z);
      const dx = cxS + (sx - cxS) * sc, dy = cyS + (sy - cyS) * sc, dw = pitch * sc;
      if (dx + dw < 0 || dy + dw < 0 || dx > W || dy > H) continue;
      ctx.drawImage(sLayer, lx * DPR, ly * DPR, px, px, dx, dy, dw, dw);
    }
    ctx.restore();
  }

  function frame(now){
    if (!running) return;
    if (!layer){ requestAnimationFrame(frame); return; }
    if (!entryStart) entryStart = now;
    const t = Math.min(1, (now - entryStart) / ENTRY_MS);
    const progress = easeOutPow4(t);
    const zb = breathZ(now);

    if (progress < 0.995){
      drawEntry(progress, zb);
    } else {
      ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
      const s = scaleForZ(zb);
      drawLayers(s, 1);
      drawLens(s, 1);
    }
    requestAnimationFrame(frame);
  }

  function startParticles(){
    resize();
    entryStart = 0;
    if (!running){ running = true; requestAnimationFrame(frame); }
  }

  window.addEventListener('resize', () => { resize(); });
  resize();

  /* =========================================================
     7. EXPLORE — the Western Cape wine map as a tilted 3D plane,
        rendered through the SAME texture × dot-screen bake as the
        hero, with pulsing gold markers on the districts (reference:
        a perspective aerial with yellow ring pointers + hover cards).
     ========================================================= */
  (function(){
    const sec = document.getElementById('explore');
    const plane = document.getElementById('mapPlane');
    const mc = document.getElementById('mapCanvas');
    const mctx = mc.getContext('2d');
    const mtex = new Image(); let mready = false;
    mtex.onload = () => { mready = true; bakeMap(); };
    mtex.src = MAP_TEX_SRC;

    // the chart's own coast, ridges and roads, redrawn over the texture at weights tied to the dot pitch
    // (the texture's lines are fixed pixels: fine on a big screen, lost between the dots on a small one)
    const CHART_BOX = { lon0: 17.6, lon1: 23.75, lat0: 31.25, lat1: 35.05 };
    function overlayGeo(g, W, H, pitch){
      if(!GEO) return;
      const P = (lon, lat) => [ (lon - CHART_BOX.lon0)/(CHART_BOX.lon1 - CHART_BOX.lon0) * W, (lat - CHART_BOX.lat0)/(CHART_BOX.lat1 - CHART_BOX.lat0) * H ];
      const stroke = (pts, alpha, width) => { g.strokeStyle = `rgba(255,255,255,${alpha})`; g.lineWidth = width; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); pts.forEach((p, i) => { const q = P(p[0], p[1]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.stroke(); };
      const k = W / 1100;
      g.save(); g.globalCompositeOperation = 'lighter';
      [[10, 0.10], [22, 0.06], [36, 0.04]].forEach(([w, al]) => stroke(GEO.coast, al, w * k));   // offshore soundings
      GEO.ridges.forEach(r => stroke(r, 0.45, Math.max(0.9, pitch * 0.45)));
      GEO.roads.forEach(r => stroke(r, 0.42, Math.max(0.9, pitch * 0.4)));
      stroke(GEO.coast, 0.9, Math.max(1.4, pitch * 0.75));
      g.restore();
    }
    function bakeMap(){
      if(!mready) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const cw = plane.clientWidth, ch = plane.clientHeight;
      if(!cw || !ch) return;
      mc.width = Math.round(cw * dpr); mc.height = Math.round(ch * dpr);
      const ny = gridRows(ch), nx = Math.round(ny * cw / ch);
      const pitch = cw / nx;
      // per-cell brightness → which cells exist at all
      const sc = document.createElement('canvas'); sc.width = nx; sc.height = ny;
      const sx = sc.getContext('2d'); sx.drawImage(mtex, 0, 0, nx, ny);
      const id = sx.getImageData(0, 0, nx, ny).data;
      // dot-screen mask
      const mask = document.createElement('canvas'); mask.width = mc.width; mask.height = mc.height;
      const mk = mask.getContext('2d'); mk.setTransform(dpr, 0, 0, dpr, 0, 0);
      const disc = makeDisc(pitch * 0.78 * dpr); const dd = disc.width / dpr;
      for(let r = 0; r < ny; r++) for(let c = 0; c < nx; c++){
        const b = id[(r * nx + c) * 4] / 255;
        if(b < 0.05 || Math.random() < 0.08) continue;
        mk.globalAlpha = 0.7 + 0.3 * Math.random();
        mk.drawImage(disc, (c + 0.5) * pitch - dd/2, (r + 0.5) * pitch - dd/2, dd, dd);
      }
      // layer = texture × mask, then a bloom pass
      const layer = document.createElement('canvas'); layer.width = mc.width; layer.height = mc.height;
      const lc = layer.getContext('2d'); lc.setTransform(dpr, 0, 0, dpr, 0, 0);
      drawFiltered(lc, mtex, { brightness: 1.25 * fineBoost(pitch), contrast: 1.1, blur: fineBlur(pitch) }, 0, 0, cw, ch);
      overlayGeo(lc, cw, ch, pitch);
      lc.setTransform(1, 0, 0, 1, 0, 0); lc.globalCompositeOperation = 'destination-in'; lc.drawImage(mask, 0, 0);
      mctx.setTransform(1, 0, 0, 1, 0, 0);
      mctx.fillStyle = '#000'; mctx.fillRect(0, 0, mc.width, mc.height);
      mctx.drawImage(layer, 0, 0);
      mctx.globalCompositeOperation = 'lighter'; mctx.globalAlpha = 0.55;
      drawFiltered(mctx, layer, { blur: Math.max(2, pitch * 0.8 * dpr), contrast: 1.5 }, 0, 0);
      mctx.globalAlpha = 1; mctx.globalCompositeOperation = 'source-over';
    }
    window.addEventListener('resize', bakeMap);
    setTimeout(bakeMap, 50);

    // reveal + mouse parallax tilt of the plane
    new IntersectionObserver((es, o)=>{ es.forEach(e=>{ if(e.isIntersecting){ sec.classList.add('visible'); setTimeout(bakeMap, 30); o.unobserve(e.target); } }); }, { threshold: 0.25 }).observe(sec);
    let tx = 0, tz = 0, cx = 0, cz = 0;
    sec.addEventListener('mousemove', e=>{
      const r = sec.getBoundingClientRect();
      tx = ((e.clientY - r.top) / r.height - 0.5) * -6;
      tz = ((e.clientX - r.left) / r.width - 0.5) * 6;
    }, { passive:true });
    sec.addEventListener('mouseleave', ()=>{ tx = 0; tz = 0; });
    (function tilt(){
      cx += (tx - cx) * 0.06; cz += (tz - cz) * 0.06;
      plane.style.transform = `translateX(-50%) rotateX(${(62 + cx).toFixed(2)}deg) rotateZ(${(-3 + cz).toFixed(2)}deg)`;
      requestAnimationFrame(tilt);
    })();

    // radar: the needle and its trail sweep clockwise on their own, slowly and without end


    /* ---- one marker per atlas region, every one of them live ---- */
    const STATUS_LABEL = {
      complete_pending_verification: 'RECORDED · AWAITING INDEPENDENT REVIEW',
      over_enumerated_pending_verification: 'RECORDED · AWAITING INDEPENDENT REVIEW',
      in_progress: 'RESEARCH IN PROGRESS', audited: 'INDEPENDENTLY REVIEWED', not_started: 'NOT YET RESEARCHED'
    };
    const card = document.getElementById('mapCard');
    const listEl = document.getElementById('regionList');
    let hideTimer = null, pinnedKey = null;
    const maxFarms = Math.max(...ATLAS.idx.map(r => r.farms));
    ATLAS.idx.forEach((r, i) => {
      const m = MAP_MARKS[r.key]; if(!m) return;
      const o = document.createElement('button');
      o.type = 'button';
      o.className = 'orb live';
      o.dataset.key = r.key;
      o.setAttribute('aria-label', `${r.name} — ${r.farms} producer${r.farms === 1 ? '' : 's'}. Open the region`);
      const sc = 0.72 + 0.55 * Math.sqrt(r.farms / maxFarms);
      o.style.left = (m[0]*100).toFixed(2) + '%'; o.style.top = (m[1]*100).toFixed(2) + '%';
      o.style.setProperty('--sc', sc.toFixed(2));
      o.innerHTML = '<i></i><i></i><i></i><i></i>';
      o.style.transitionDelay = (0.04 * i) + 's';
      plane.appendChild(o);
      const li = document.createElement('button');
      li.type = 'button';
      li.className = 'rl'; li.dataset.key = r.key;
      li.setAttribute('aria-label', `${r.name} — ${r.farms} producer${r.farms === 1 ? '' : 's'}. Open the region`);
      li.innerHTML = `<span class="n">${String(i+1).padStart(2,'0')} ${r.name.toUpperCase()}</span><span class="c">${r.farms}</span>`;
      listEl.appendChild(li);
      const show = () => {
        clearTimeout(hideTimer);
        document.querySelectorAll('.orb.hi, .rl.hi').forEach(e => e.classList.remove('hi'));
        o.classList.add('hi'); li.classList.add('hi');
        document.getElementById('mcEyebrow').textContent = `${r.woRegion.toUpperCase()} · ${r.district.toUpperCase()}${/DISTRICT|REGION|—/.test(r.district.toUpperCase()) ? '' : ' DISTRICT'}`;
        document.getElementById('mcName').textContent = r.name;
        document.getElementById('mcText').innerHTML = `<div class="stat mono">
          <span>PRODUCERS ON RECORD</span><b>${r.farms}</b>
          <span>WITH A LOCATION</span><b>${r.pinned}</b>
          <span>HONOURS VERIFIED</span><b>${r.awards}</b>
          <span>CLAIMS UNDER REVIEW</span><b>${r.pending}</b>
          <span>AWARD RESEARCH</span><b>${r.researched} / ${r.farms}</b>
          ${r.withheld ? `<span>HELD BACK UNTIL THEY MEET THE STANDARD</span><b>${r.withheld}</b>` : ''}
          <span>STATUS</span><b>${STATUS_LABEL[r.status] || r.status.toUpperCase()}</b>
        </div><div class="cta mono">OPEN THE REGION ▸</div>`;
        document.getElementById('mcTags').innerHTML = '';
        card.classList.add('show');
      };
      const hide = () => {
        if(pinnedKey === r.key) return;
        hideTimer = setTimeout(() => { o.classList.remove('hi'); li.classList.remove('hi'); card.classList.remove('show'); }, 380);
      };
      o.addEventListener('mouseenter', show); o.addEventListener('mouseleave', hide);
      li.addEventListener('mouseenter', show); li.addEventListener('mouseleave', hide);
      o.addEventListener('focus', show); o.addEventListener('blur', hide); li.addEventListener('focus', show); li.addEventListener('blur', hide);
      li.addEventListener('click', () => openRegion(r.key));
    });
    // A press on the chart opens the marker nearest the finger or pointer, measured on screen after the
    // 3-D projection — so in the dense Stellenbosch / Cape Town cluster, and on a phone-sized chart,
    // the marker you aimed at wins rather than whichever overlapping hit-area happens to sit on top.
    plane.addEventListener('click', e => {
      if (e.detail === 0){ const o = e.target.closest('.orb'); if (o){ e.stopPropagation(); openRegion(o.dataset.key); } return; }   // keyboard
      let best = null, bd = Infinity;
      plane.querySelectorAll('.orb').forEach(o => {
        const b = o.getBoundingClientRect();
        const dx = b.left + b.width / 2 - e.clientX, dy = b.top + b.height / 2 - e.clientY, d = dx * dx + dy * dy;
        if (d < bd){ bd = d; best = o; }
      });
      if (best && bd <= 44 * 44){ e.stopPropagation(); openRegion(best.dataset.key); }
    });
    card.addEventListener('mouseenter', () => clearTimeout(hideTimer));
    card.addEventListener('mouseleave', () => { if(!pinnedKey) hideTimer = setTimeout(() => card.classList.remove('show'), 380); });
  })();

  /* =========================================================
     8. REGION VIEW — a full-screen readout for any region,
        rendered straight from the atlas record. The tactical
        map is drawn in the browser from the coast / ridge / road
        geometry and the producers' own coordinates, then passed
        through the same dot-screen bake as the hero.
     ========================================================= */
  const rv = document.getElementById('regionView');
  const rvScroll = document.getElementById('rvScroll');
  const ACCESS = { walk_in:'WALK-IN TASTING', appointment:'TASTING BY APPOINTMENT', scheduled:'TASTING ON ANNOUNCED DATES', closed_temporarily:'TASTING CLOSED FOR NOW', closed_permanently:'TASTING PERMANENTLY CLOSED', none:'NO TASTING ROOM', unknown:'ACCESS NOT CONFIRMED' };
  const STATUS_LABEL_RV = { complete_pending_verification:'recorded · awaiting independent review', over_enumerated_pending_verification:'recorded · awaiting independent review', in_progress:'research in progress', audited:'independently reviewed', not_started:'not yet researched' };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const host = u => { try { return new URL(u).hostname.replace(/^www\./,''); } catch(e){ return u; } };
  const shortName = n => n.replace(/ \(.*\)$/,'').replace(/ (Estate|Vineyards|Wines|Wine Estate|Wine Cellar|Organic Wine Estate|Family Wines|Winery|Wine Farm|Private Cellar)$/,'');

  // ---------- tactical map: geometry → canvas ----------
  let tacticalBox = null, tacticalPins = {};
  function regionBox(R){
    const pts = R.farms.filter(f => f.lat != null);
    let lon0, lon1, lat0, lat1;
    if(pts.length){
      lon0 = Math.min(...pts.map(f=>f.lng)); lon1 = Math.max(...pts.map(f=>f.lng));
      lat0 = Math.min(...pts.map(f=>-f.lat)); lat1 = Math.max(...pts.map(f=>-f.lat));
    } else {
      const i = ATLAS.idx.find(x => x.key === R.key); lon0 = lon1 = i.lng; lat0 = lat1 = -i.lat;
    }
    const KX = Math.cos(33.9 * Math.PI/180);
    let w = Math.max((lon1 - lon0) * 1.5, pts.length ? 0.09 : 0.6), h = Math.max((lat1 - lat0) * 1.5, pts.length ? 0.075 : 0.5);
    // fit the mini-map's portrait frame (760:915) in km terms
    const target = (760/915);
    if((w*KX)/h > target) h = (w*KX)/target; else w = (h*target)/KX;
    const cx = (lon0+lon1)/2, cy = (lat0+lat1)/2;
    return { lon0: cx - w/2, lon1: cx + w/2, lat0: cy - h/2, lat1: cy + h/2 };
  }
  function drawTactical(cv, R, box, pitchTex){
    const W = cv.width, H = cv.height, g = cv.getContext('2d');
    // line weights: the drawing was tuned at 760 px wide; scale with the canvas, and never thinner than a
    // good fraction of a dot, so the coast, ridges and roads survive the dot-screen on a small screen
    const k = W / 760, pt = pitchTex || 0;
    const lw = (base, frac) => Math.max(base * k, frac * pt);
    const P = (lon, lat) => [ (lon - box.lon0)/(box.lon1 - box.lon0) * W, (lat - box.lat0)/(box.lat1 - box.lat0) * H ];
    const rnd = (() => { let s = 7; return () => { s = (s * 16807) % 2147483647; return s / 2147483647; }; })();
    g.fillStyle = '#000'; g.fillRect(0,0,W,H);
    // land mask from the coast polygon (everything north/east of the coast is land)
    const land = GEO.coast.map(p => P(p[0], p[1]));
    land.push(P(23.75, 31.25), P(17.85, 31.25));
    const landPath = new Path2D(); land.forEach((p,i) => i ? landPath.lineTo(p[0],p[1]) : landPath.moveTo(p[0],p[1])); landPath.closePath();
    g.save(); g.clip(landPath);
    g.fillStyle = 'rgba(255,255,255,0.3)';
    const sp = lw(1.4, 0.3);
    for(let i=0;i<W*H/380;i++){ g.globalAlpha = 0.5 + 0.5*rnd(); g.fillRect(rnd()*W, rnd()*H, sp, sp); }
    g.globalAlpha = 1; g.restore();
    const smooth = pts => { const out=[]; for(let i=0;i<pts.length-1;i++){ const a=pts[i], b=pts[i+1]; for(let t=0;t<1;t+=0.1) out.push([a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t]); } out.push(pts[pts.length-1]); return out; };
    const line = (pts, alpha, width, dash) => {
      const q = smooth(pts.map(p => P(p[0], p[1])));
      g.strokeStyle = `rgba(255,255,255,${alpha})`; g.lineWidth = width; g.lineCap = 'round';
      if(dash){ for(let i=0;i<q.length-1;i++){ if(rnd() < dash){ g.beginPath(); g.moveTo(q[i][0],q[i][1]); g.lineTo(q[i+1][0],q[i+1][1]); g.stroke(); } } return q; }
      g.beginPath(); q.forEach((p,i) => i ? g.lineTo(p[0],p[1]) : g.moveTo(p[0],p[1])); g.stroke(); return q;
    };
    // offshore soundings: three faint dotted echoes of the coast, offset seaward is hard — use dashed parallel strokes via wider translucent lines
    g.save(); g.globalCompositeOperation = 'destination-over';
    [[10,0.10],[22,0.06],[36,0.04]].forEach(([w,a]) => line(GEO.coast, a, w * k, 0));
    g.restore();
    // ridges: hatched
    GEO.ridges.forEach(r => {
      const q = line(r, 0.55, lw(1.2, 0.45), 0);
      for(let i=0;i<q.length-1;i+=3){
        const a=q[i], b=q[i+1]; let nx=-(b[1]-a[1]), ny=b[0]-a[0]; const l=Math.hypot(nx,ny)||1; nx/=l; ny/=l;
        const L = (W/26) * (0.5 + rnd());
        g.strokeStyle = `rgba(255,255,255,${0.35+0.4*rnd()})`; g.lineWidth = lw(1, 0.35);
        g.beginPath(); g.moveTo(a[0]-nx*L*0.2, a[1]-ny*L*0.2); g.lineTo(a[0]+nx*L, a[1]+ny*L); g.stroke();
      }
    });
    GEO.roads.forEach(r => line(r, 0.55, lw(1, 0.4), 0));
    line(GEO.coast, 1, lw(2.6, 0.7), 0);
    // vineyard stipple around each producer
    R.farms.filter(f => f.lat != null).forEach(f => {
      const [x,y] = P(f.lng, -f.lat); const rx = W*(0.035+0.03*rnd()), ry = rx*(0.6+0.4*rnd()), rot = rnd()*Math.PI;
      for(let i=0;i<220;i++){ const a=rnd()*Math.PI*2, d=Math.sqrt(rnd()); const px=Math.cos(a)*rx*d, py=Math.sin(a)*ry*d;
        const sq = lw(1.5, 0.32); g.fillStyle = `rgba(255,255,255,${0.45+0.55*rnd()})`; g.fillRect(x+px*Math.cos(rot)-py*Math.sin(rot), y+px*Math.sin(rot)+py*Math.cos(rot), sq, sq); }
    });
    // graticule
    const span = box.lon1 - box.lon0; const step = span > 1.2 ? 0.5 : span > 0.5 ? 0.2 : span > 0.2 ? 0.1 : 0.02;
    g.fillStyle = 'rgba(255,255,255,0.3)';
    const gq = lw(1, 0.25), gs = Math.max(3, Math.round(3 * k));
    for(let lon = Math.ceil(box.lon0/step)*step; lon < box.lon1; lon += step){ const x = P(lon,0)[0]; for(let y=0;y<H;y+=gs) if(rnd()<0.35) g.fillRect(x, y, gq, gq); }
    for(let lat = Math.ceil(box.lat0/step)*step; lat < box.lat1; lat += step){ const y = P(0,lat)[1]; for(let x=0;x<W;x+=gs) if(rnd()<0.35) g.fillRect(x, y, gq, gq); }
    // edge fade
    const fade = g.createLinearGradient(0,0,W,0); fade.addColorStop(0,'rgba(0,0,0,.9)'); fade.addColorStop(.12,'rgba(0,0,0,0)'); fade.addColorStop(.88,'rgba(0,0,0,0)'); fade.addColorStop(1,'rgba(0,0,0,.9)');
    g.fillStyle = fade; g.fillRect(0,0,W,H);
    const fadeV = g.createLinearGradient(0,0,0,H); fadeV.addColorStop(0,'rgba(0,0,0,.9)'); fadeV.addColorStop(.1,'rgba(0,0,0,0)'); fadeV.addColorStop(.9,'rgba(0,0,0,0)'); fadeV.addColorStop(1,'rgba(0,0,0,.9)');
    g.fillStyle = fadeV; g.fillRect(0,0,W,H);
    return P;
  }
  function bakeMini(R){
    const cv = document.getElementById('miniCanvas'); if(!cv) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const cw = cv.clientWidth, ch = cv.clientHeight; if(!cw || !ch) return;
    cv.width = Math.round(cw*dpr); cv.height = Math.round(ch*dpr);
    const x = cv.getContext('2d');
    const ny = gridRows(ch, 3.6), nx = Math.round(ny * cw / ch), pitch = cw / nx;
    // the tactical drawing is made at the canvas's own resolution, with its line weights tied to the dot pitch
    const tex = document.createElement('canvas'); tex.width = Math.max(760, cv.width); tex.height = Math.round(tex.width * ch / cw);
    drawTactical(tex, R, tacticalBox, pitch * tex.width / cw);
    const sc = document.createElement('canvas'); sc.width = nx; sc.height = ny;
    const sx = sc.getContext('2d'); sx.drawImage(tex, 0, 0, nx, ny);
    const id = sx.getImageData(0, 0, nx, ny).data;
    const mask = document.createElement('canvas'); mask.width = cv.width; mask.height = cv.height;
    const mk = mask.getContext('2d'); mk.setTransform(dpr,0,0,dpr,0,0);
    const disc = makeDisc(pitch * 0.78 * dpr), dd = disc.width / dpr;
    for(let r=0;r<ny;r++) for(let c=0;c<nx;c++){
      if(id[(r*nx+c)*4]/255 < 0.05 || Math.random() < 0.08) continue;
      mk.globalAlpha = 0.7 + 0.3*Math.random();
      mk.drawImage(disc, (c+.5)*pitch - dd/2, (r+.5)*pitch - dd/2, dd, dd);
    }
    const layer = document.createElement('canvas'); layer.width = cv.width; layer.height = cv.height;
    const lc = layer.getContext('2d'); lc.setTransform(dpr,0,0,dpr,0,0);
    drawFiltered(lc, tex, { brightness: 1.6 * fineBoost(pitch), contrast: 1.15, blur: fineBlur(pitch) }, 0, 0, cw, ch);
    lc.setTransform(1,0,0,1,0,0); lc.globalCompositeOperation = 'destination-in'; lc.drawImage(mask, 0, 0);
    x.fillStyle = '#000'; x.fillRect(0,0,cv.width,cv.height);
    x.drawImage(layer, 0, 0);
    x.globalCompositeOperation = 'lighter'; x.globalAlpha = 0.65;
    drawFiltered(x, layer, { blur: Math.max(2, pitch*0.8*dpr), contrast: 1.5 }, 0, 0);
    x.globalAlpha = 1; x.globalCompositeOperation = 'source-over';
    const kmAcross = (tacticalBox.lon1 - tacticalBox.lon0) * 111.32 * Math.cos(33.9*Math.PI/180);
    const sb = document.querySelector('#rvMap .scale'); if(sb){ const km = kmAcross > 40 ? 10 : kmAcross > 12 ? 5 : 1; sb.querySelector('i').style.width = (cw * km / kmAcross).toFixed(1) + 'px'; sb.querySelector('span').textContent = `≈ ${km} KM`; }
  }

  let currentRegion = null;
  function renderRegion(R){
    currentRegion = R;
    const S = ATLAS.stats, farms = R.farms;
    const pinned = farms.filter(f => f.lat != null).length;
    const awards = farms.reduce((n,f) => n + f.awards.length, 0);
    const pending = farms.reduce((n,f) => n + (f.pendingClaims||0), 0);
    const researched = farms.filter(f => f.awardsCollected).length;
    const walkIn = farms.filter(f => f.access === 'walk_in').length;
    const founded = farms.filter(f => f.founded).map(f => f.founded);
    const oldest = founded.length ? Math.min(...founded) : null;
    const wards = [...new Set(farms.map(f => f.ward).filter(Boolean))];
    tacticalBox = regionBox(R);
    const Pn = (lon, lat) => [ (lon - tacticalBox.lon0)/(tacticalBox.lon1 - tacticalBox.lon0) * 100, (lat - tacticalBox.lat0)/(tacticalBox.lat1 - tacticalBox.lat0) * 100 ];
    const showLabels = pinned <= 16;
    const located = farms.filter(f => f.lat != null).map(f => ({ f, p: Pn(f.lng, -f.lat) })).sort((a,b) => a.p[1] - b.p[1]);
    let prev = null;
    const pins = located.map(({f, p}) => {
      let side = p[0] < 55 ? 'r' : 'l', dy = 0;
      if(prev && Math.abs(prev.p[1] - p[1]) < 3.2 && Math.abs(prev.p[0] - p[0]) < 30){ dy = prev.dy <= 0 ? 9 : -9; side = prev.side === 'r' ? 'l' : 'r'; }
      prev = { p, dy, side };
      return `<button type="button" class="pin${showLabels ? '' : ' quiet'}" data-id="${f.id}" aria-label="Show the record for ${esc(f.name)}" style="left:${p[0].toFixed(2)}%;top:${p[1].toFixed(2)}%"><i></i><i></i><i></i><b class="${side}" style="margin-top:${dy}px">${esc(shortName(f.name))}</b></button>`;
    }).join('');

    const ward = R.ward && !/\(/.test(R.ward) ? R.ward : null;
    const chain = [R.woRegion, R.district].filter(x => x && x !== '—' && x.toUpperCase() !== R.name.toUpperCase());
    const chainTxt = chain.map(x => esc(x.toUpperCase()));
    document.getElementById('rvCrumb').innerHTML = `<b>CAPE WINE ATLAS</b>${chainTxt.map(x => `<span>/</span>${x}`).join('')}<span>/</span><b>${esc((ward || R.name).toUpperCase())}${ward ? ' WARD' : ''}</b>`;

    const recs = farms.map(f => {
      const meta = [
        f.founded ? `EST ${f.founded}` : null,
        `<span class="${(f.access==='walk_in'||f.access==='appointment')?'ok':''}">${ACCESS[f.access] || 'ACCESS NOT CONFIRMED'}</span>`,
        (f.ward && (!R.ward || f.ward !== R.ward)) ? `WARD · ${esc(f.ward.toUpperCase())}` : (f.locality && !f.ward ? esc(f.locality.split(/[(—]/)[0].trim().toUpperCase()) : null),
        f.routeMember === 'yes' ? 'ROUTE MEMBER' : null,
        f.lat != null ? `LOCATION · ${String(f.geoConfidence||'').toUpperCase()}` : 'LOCATION NOT YET RESOLVED',
        f.oldVineFlag ? '<span class="gold">OLD VINES</span>' : null
      ].filter(Boolean).map(x => `<span>${x}</span>`).join('');
      const led = f.awards.map(a => `<div class="aw"><span class="y">${a.year ?? '—'}</span><span><b>${esc(a.body)}</b> — ${esc(a.award)}<br><span class="w">${esc(a.wine)}</span>${a.sourceUrl ? `<br><a class="src mono" href="${esc(a.sourceUrl)}" target="_blank" rel="noopener" title="${esc(a.sourceName || '')}">SOURCE · ${esc((a.sourceName ? (a.sourceName.length <= 32 ? a.sourceName : a.sourceName.slice(0, 30).replace(/[\s—–-]+$/,'') + '…') : host(a.sourceUrl)).toUpperCase())}</a>` : ''}${a.corr ? '<span class="corr mono" title="Held in two independent competitions">✓✓ CORROBORATED</span>' : ''}</span></div>`).join('');
      const flags = [
        !f.awardsCollected ? '<span class="flag warn mono">AWARDS NOT YET RESEARCHED</span>' : '',
        f.awardsCollected && !f.awards.length && !f.pendingClaims ? '<span class="flag dim mono">NO VERIFIED HONOUR ON FILE</span>' : '',
        f.pendingClaims ? `<span class="flag gold mono">${f.pendingClaims} CLAIM${f.pendingClaims>1?'S':''} UNDER REVIEW</span>` : ''
      ].join('');
      const contact = [
        f.web ? `<a href="${esc(f.web)}" target="_blank" rel="noopener">${esc(host(f.web))}</a>` : '',
        f.contactHeld ? `<span title="On file, not republished — reach the producer through its own site">${esc(f.contactHeld.toUpperCase())} ON FILE · NOT REPUBLISHED</span>` : ''
      ].filter(Boolean).join('');
      const hay = [f.name, f.ward, f.locality, ...(f.varieties||[]), ...(f.signatureWines||[])].join(' ').toLowerCase();
      return `<article class="rec" id="rec-${f.id}" data-id="${f.id}" data-hay="${esc(hay)}" data-awarded="${f.awards.length ? 1 : 0}">
        <div class="rec-bar mono"><span>$ record.${f.id}</span><span class="term-dots"><span></span><span></span><span></span></span></div>
        <div class="rec-body">
          <div class="rec-name display">${esc(f.name)}</div>
          <div class="rec-meta mono">${meta}</div>
          ${f.history ? `<p class="rec-hist">${esc(f.history)}</p>` : ''}
          ${f.people ? `<div class="rec-row"><span class="k mono">PEOPLE</span><span>${esc(f.people)}</span></div>` : ''}
          ${f.hours ? `<div class="rec-row"><span class="k mono">HOURS</span><span>${esc(f.hours)}</span></div>` : ''}
          ${f.varieties && f.varieties.length ? `<div class="rec-row"><span class="k mono">VARIETIES</span><div class="tags mono">${f.varieties.map(v=>`<span>${esc(v)}</span>`).join('')}</div></div>` : ''}
          ${f.signatureWines && f.signatureWines.length ? `<div class="rec-row"><span class="k mono">SIGNATURE</span><span>${f.signatureWines.map(esc).join(' · ')}</span></div>` : ''}
          <div class="rec-awards">${led}${flags}</div>
          <div class="rec-contact mono">${contact}</div>
        </div></article>`;
    }).join('');

    const routes = R.routes.length ? R.routes.map(rt => `
      <p><b>${esc(rt.name)}</b>${rt.area ? ` — ${esc(rt.area)}` : ''}. ${rt.membersRecorded != null ? `${rt.membersRecorded}${rt.membersExpected ? ` of ${rt.membersExpected}` : ''} members on record; ` : ''}membership ${esc(rt.status === 'verified' ? 'confirmed against the route’s own listing' : rt.status === 'no_association' ? 'not applicable — no association exists' : 'still being confirmed')}.${rt.blurb ? ' ' + esc(rt.blurb.replace(/;$/, '.')) : ''}</p>
      ${rt.sourceUrl ? `<p class="mono" style="font-size:10px;letter-spacing:.12em;color:var(--muted)">SOURCE · <a style="color:inherit" href="${esc(rt.sourceUrl)}" target="_blank" rel="noopener">${esc(host(rt.sourceUrl))}</a>${rt.retrieved ? ` · CONSULTED ${esc(rt.retrieved)}` : ''}</p>` : ''}`).join('')
      : `<p>No route association is on file for this area; the producers below were gathered from the wine industry’s own records and their own websites.</p>`;
    const tours = R.tours.length ? R.tours.map(t => `<div class="tour"><b>${esc(t.name)}</b>${t.verified ? '' : ' <span class="flag dim mono">NOT YET CONFIRMED</span>'}<span class="t mono">${esc(t.type)} · ${esc(t.base)}${t.web ? ` · <a href="${esc(t.web)}" target="_blank" rel="noopener">${esc(host(t.web))}</a>` : ''}</span></div>`).join('')
      : `<div class="tour"><span class="t mono">NO TOUR OPERATOR IS YET LISTED FOR THIS ROUTE</span></div>`;
    const compList = S.competitions.map(c => `${esc(c.body)} ${c.year}`).join(' · ');

    rvScroll.innerHTML = `
      <div class="rv-head">
        <div>
          <div class="rv-eyebrow mono">${[...chainTxt, ward ? esc(ward.toUpperCase()) + ' WARD' : null, R.routes[0] ? esc(R.routes[0].name.toUpperCase()) : null].filter(Boolean).join(' · ') || 'WESTERN CAPE'}</div>
          <h2 class="display" id="rvTitle" tabindex="-1">${esc(R.name)}</h2>
          <p class="rv-lede" id="rvLede"></p>
          <div class="rv-stats mono">
            <div><span class="v">${farms.length}</span><span class="k">PRODUCERS ON RECORD</span></div>
            <div><span class="v">${pinned}</span><span class="k">WITH A LOCATION</span></div>
            <div><span class="v g">${awards}</span><span class="k">HONOURS VERIFIED</span></div>
            <div><span class="v">${pending}</span><span class="k">CLAIMS UNDER REVIEW</span></div>
            <div><span class="v">${researched}/${farms.length}</span><span class="k">AWARD RESEARCH COMPLETE</span></div>
            <div><span class="v">${walkIn}</span><span class="k">WALK-IN TASTING ROOMS</span></div>
            <div><span class="v">${oldest ?? '—'}</span><span class="k">OLDEST FOUNDING ON FILE</span></div>
            <div><span class="v">${wards.length || '—'}</span><span class="k">${wards.length === 1 ? 'WARD' : 'WARDS'} REPRESENTED</span></div>
          </div>
          ${R.withheld ? `<div class="rv-withheld mono">${R.withheld} FURTHER ${R.withheld === 1 ? 'RECORD IS' : 'RECORDS ARE'} HELD BACK UNTIL ${R.withheld === 1 ? 'IT MEETS' : 'THEY MEET'} THE PUBLICATION STANDARD</div>` : ''}
        </div>
        <div class="rv-map" id="rvMap">
          <canvas id="miniCanvas" role="img" aria-label="Tactical map of ${esc(R.name)}: producers with a published position"></canvas>
          <span class="corner tl"></span><span class="corner br"></span>
          <div class="hud mono">TACTICAL · ${esc(R.name.toUpperCase())}<br><b>${pinned}/${farms.length}</b> POSITIONS LOCATED${pinned < farms.length ? `<br>${farms.length - pinned} AWAITING A PUBLISHED POSITION` : ''}</div>
          ${pins}
          ${pinned ? '' : '<div class="nopins mono">NO PUBLISHED POSITION YET<br>FOR THESE PRODUCERS</div>'}
          <div class="scale mono"><i style="width:60px"></i><span>≈ 1 KM</span></div>
        </div>
      </div>

      <section class="rv-block">
        <h3 class="mono"><span class="h3l">PRODUCER RECORDS <span>${farms.length} ON RECORD · ${esc((STATUS_LABEL_RV[R.status]||R.status).toUpperCase())}</span></span>
          <span class="h3r"><input class="mono" id="recFilter" placeholder="FILTER · NAME, WARD, GRAPE" aria-label="Filter producers by name, ward or grape" autocomplete="off"><label class="mono"><input type="checkbox" id="recAwarded"> HONOURS ONLY</label></span></h3>
        <div class="rv-grid" id="recGrid">${recs}</div>
        <div class="rv-empty mono" id="recEmpty" hidden>NO RECORD MATCHES THAT FILTER</div>
      </section>

      <section class="rv-block rv-two">
        <div>
          <h4 class="mono">THE ROUTE</h4>
          ${routes}
          <h4 class="mono" style="margin-top:26px">TOUR OPERATORS SERVING THIS AREA · ${R.tours.length}</h4>
          <div class="rv-note" style="margin-bottom:10px"><b>LISTED, NOT ENDORSED.</b> An operator appears here because it publicly offers winelands tours and we can point to where it says so. Inclusion says nothing about licensing, insurance or safety — please confirm operating permits and current schedules with the operator directly. Details are as published at the source on the day we consulted it.</div>
          ${tours}
        </div>
        <div>
          <h4 class="mono">THE HONOURS LEDGER</h4>
          <p>${researched === farms.length ? 'Every producer in this region has had its honours researched' : `${researched} of the ${farms.length} producers here have had their honours researched so far`}: ${awards} ${awards === 1 ? 'award stands' : 'awards stand'} verified against ${awards === 1 ? 'its source' : 'their sources'}${pending ? `, and ${pending} further ${pending === 1 ? 'claim waits' : 'claims wait'} for confirmation` : ''}. Competitions consulted: ${compList}.</p>
          <h4 class="mono" style="margin-top:26px">HOW TO READ THIS PAGE</h4>
          <div class="rv-note">
            <b>NOTHING IS WRITTEN HERE WITHOUT A SOURCE.</b> Every honour links to the page where it was found. Our researchers may only record what they can cite; an entry is promoted to “confirmed” only once a second, independent reviewer has gone back to the source.<br><br>
            <b>“NOT YET RESEARCHED” IS NOT “NO AWARDS”.</b> The atlas is careful to tell “nobody has looked yet” apart from “nothing was won” — many fine producers simply never enter competitions.<br><br>
            <b>WHAT IS HELD BACK.</b> Where a detail rests on a source the atlas is not free to republish, it is withheld until the producer’s own site or an open record confirms it. Claims still under review are counted, never presented as fact.
          </div>
          ${R.terroir && R.lede !== R.terroir ? `<h4 class="mono" style="margin-top:26px">TERROIR</h4><p>${esc(R.terroir)}</p>` : ''}
        </div>
      </section>

      <div class="rv-foot mono">
        <span>THE ATLAS RECORD · ${esc(EDITION)}</span><span>DATA UNDER ODbL 1.0 · CONTAINS INFORMATION FROM OPENSTREETMAP, © OPENSTREETMAP CONTRIBUTORS</span><span>${[...chainTxt, ward ? esc(ward.toUpperCase()) : null].filter(Boolean).join(' · ') || esc(R.name.toUpperCase())}</span><span>RECORDS GATHERED ${esc(R.collected || '—')}</span><span>ACROSS THE ATLAS · ${S.farms} FARMS · ${S.regions} REGIONS · ${S.verifiedAwards} HONOURS VERIFIED</span>
      </div>`;

    // pin ↔ record highlighting
    rvScroll.querySelectorAll('.pin').forEach(p => {
      const rec = rvScroll.querySelector('#rec-' + p.dataset.id);
      p.addEventListener('mouseenter', () => { rec && rec.classList.add('hi'); });
      p.addEventListener('mouseleave', () => { rec && rec.classList.remove('hi'); });
      p.addEventListener('click', () => { if(!rec) return; rec.scrollIntoView({ behavior: REDUCED_MOTION ? 'auto' : 'smooth', block:'center' }); rec.classList.add('hi'); setTimeout(() => rec.classList.remove('hi'), 1600); });
    });
    rvScroll.querySelectorAll('.rec').forEach(r => {
      const pin = rvScroll.querySelector(`.pin[data-id="${r.dataset.id}"]`);
      r.addEventListener('mouseenter', () => pin && pin.classList.add('hi'));
      r.addEventListener('mouseleave', () => pin && pin.classList.remove('hi'));
    });
    // filter
    const fi = document.getElementById('recFilter'), fa = document.getElementById('recAwarded');
    const applyFilter = () => {
      const q = fi.value.trim().toLowerCase(); let n = 0;
      rvScroll.querySelectorAll('.rec').forEach(r => { const ok = (!q || r.dataset.hay.includes(q)) && (!fa.checked || r.dataset.awarded === '1'); r.hidden = !ok; if(ok) n++; });
      document.getElementById('recEmpty').hidden = n > 0;
    };
    fi.addEventListener('input', applyFilter); fa.addEventListener('change', applyFilter);
  }

  window.addEventListener('resize', () => { if(rv.classList.contains('open') && currentRegion) bakeMini(currentRegion); });

  let rvOpen = false, rvKey = null;
  function regionPath(key){ return ROOT + 'region/' + key + '/'; }
  /* ---- dialogs: focus goes in, stays in, and comes back out ---- */
  const BEHIND = () => [document.getElementById('main'), document.getElementById('footer'), document.getElementById('chrome')].filter(Boolean);
  let rvOpener = null, lvOpener = null;
  function setBehindInert(on){ BEHIND().forEach(el => { el.inert = on; if(on) el.setAttribute('aria-hidden', 'true'); else el.removeAttribute('aria-hidden'); }); }
  function trapTab(dialog){
    dialog.addEventListener('keydown', e => {
      if(e.key !== 'Tab') return;
      const f = [...dialog.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), summary, [tabindex]:not([tabindex="-1"])')].filter(el => el.offsetParent !== null || el === document.activeElement);
      if(!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if(e.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))){ e.preventDefault(); last.focus(); }
      else if(!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
    });
  }
  trapTab(rv);
  const menuBtn = document.getElementById('menuToggle');
  if(menuBtn) menuBtn.addEventListener('click', () => { try { if(document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); } catch(e){} });

  async function openRegion(key, opts){
    opts = opts || {};
    if(rvOpen && rvKey === key) return;
    let R; try { R = await loadRegion(key); } catch(e){ console.warn(e); return; }
    if(!rvOpen) rvOpener = document.activeElement;
    rvOpen = true; rvKey = key;
    renderRegion(R);
    rv.classList.add('open');
    setBehindInert(true);
    document.body.style.overflow = 'hidden';
    rvScroll.scrollTop = 0;
    const title = document.getElementById('rvTitle'); if(title) title.focus({ preventScroll: true });
    if(!opts.fromHistory && location.pathname !== regionPath(key)){ push({ region: key }, regionPath(key)); }
    document.title = R.name + ' — Cape Wine Atlas';
    const boot = document.getElementById('rvBoot'), lines = document.getElementById('rvBootLines');
    boot.classList.remove('done');
    if(opts.instant){ boot.classList.add('done'); bakeMini(R); typewrite(document.getElementById('rvLede'), R.lede, 8); return; }
    const pinned = R.farms.filter(f=>f.lat!=null).length;
    const msgs = [
      `&gt;&gt; LINKING CAPE WINE ATLAS ............ <span class="g">DONE</span>`,
      `&gt;&gt; OPENING ${R.name.toUpperCase()} ......... <span class="g">${R.farms.length} RECORDS</span>`,
      `&gt;&gt; WINE OF ORIGIN: ${[R.woRegion, R.district, R.ward].filter(x => x && x !== '—').map(x => x.toUpperCase()).join(' / ') || R.name.toUpperCase()}`,
      `&gt;&gt; POSITIONS LOCATED ................. <span class="g">${pinned}/${R.farms.length}</span>`,
      `&gt;&gt; PROVENANCE CHECK ................... <span class="g">EVERY HONOUR SOURCED</span>`,
      `&gt;&gt; DRAWING THE TACTICAL MAP ...`
    ];
    lines.innerHTML = msgs.map(m => `<div>${m}</div>`).join('');
    [...lines.children].forEach((el, i) => setTimeout(() => el.classList.add('show'), 120 + i*170));
    setTimeout(() => { boot.classList.add('done'); bakeMini(R); typewrite(document.getElementById('rvLede'), R.lede, 12); }, 120 + msgs.length*170 + 350);
  }
  function closeRegion(opts){
    opts = opts || {};
    rv.classList.remove('open'); document.body.style.overflow = ''; rvOpen = false; rvKey = null;
    if(!lv.classList.contains('open')) setBehindInert(false);
    const ex = document.getElementById('explore'); if(ex) ex.scrollIntoView({ block: 'start', behavior: 'auto' });   // back to the chart, exactly, on every screen
    document.title = 'Cape Wine Atlas';
    const back = rvOpener && document.contains(rvOpener) && rvOpener !== document.body ? rvOpener : document.querySelector('#regionList .rl');
    if(back) back.focus({ preventScroll: true });
    rvOpener = null;
    if(!opts.fromHistory && location.pathname !== ROOT){ push({}, ROOT + '#explore'); }
  }
  window.addEventListener('popstate', e => {
    const m = location.pathname.match(/\/region\/([a-z0-9-]+)\/?$/);
    if(m) openRegion(m[1], { fromHistory: true, instant: true }); else if(rvOpen) closeRegion({ fromHistory: true });
  });
  document.getElementById('rvClose').addEventListener('click', closeRegion);
  /* ---- licence & credits view ---- */
  const lv = document.getElementById('licenceView');
  function openLicence(){ if(!lv.classList.contains('open')) lvOpener = document.activeElement; lv.classList.add('open'); setBehindInert(true); document.body.style.overflow = 'hidden'; lv.querySelector('.rv-scroll').scrollTop = 0; if(location.hash !== '#licence') push({ licence: true }, ROOT + '#licence'); const t = document.getElementById('lvTitle'); if(t) t.focus({ preventScroll: true }); }
  function closeLicence(){ lv.classList.remove('open'); if(!rvOpen){ document.body.style.overflow = ''; setBehindInert(false); } if(location.hash === '#licence') push({}, ROOT + '#explore'); const back = lvOpener && document.contains(lvOpener) ? lvOpener : document.getElementById('openLicence'); if(back) back.focus({ preventScroll: true }); lvOpener = null; }
  trapTab(lv);
  window.addEventListener('hashchange', () => { if(location.hash === '#licence'){ if(!lv.classList.contains('open')) openLicence(); } else if(lv.classList.contains('open')) closeLicence(); });
  document.getElementById('openLicence').addEventListener('click', e => { e.preventDefault(); openLicence(); });
  document.getElementById('lvClose').addEventListener('click', closeLicence);
  window.addEventListener('keydown', e => { if(e.key === 'Escape' && lv.classList.contains('open')) closeLicence(); });
  if(location.hash === '#licence') openLicence();

  window.addEventListener('keydown', e => { if(e.key === 'Escape' && rvOpen) closeRegion(); });

  /* =========================================================
     9. LIVE PROGRESS TERMINAL — the atlas status window types
        itself on, fills its gauges, then keeps a scanning
        ticker running through the regions.
     ========================================================= */
  (function(){
    const S = ATLAS.stats, body = document.getElementById('termBody');
    let started = false;
    function bar(p){ const n = Math.round(p*12); return '<span class="gold">' + '█'.repeat(n) + '</span><span class="grey">' + '░'.repeat(12-n) + '</span>'; }
    function countTo(el, target, ms, fmt){ const t0 = performance.now(); (function f(){ const k = Math.min(1,(performance.now()-t0)/ms); const e = 1-Math.pow(1-k,3); el.textContent = fmt(Math.round(target*e)); if(k<1) requestAnimationFrame(f); })(); }
    function start(){
      if(started) return; started = true;
      const L = [
        `<div class="grey">// CAPE WINE ATLAS — ${EDITION}</div>`,
        `<div>&gt; OPENING THE ATLAS RECORD .... <span id="tb1">${bar(0)}</span> <span class="gold" id="tc1">0</span> FARMS</div>`,
        `<div>&gt; REGIONS INDEXED ............. <span id="tb2">${bar(0)}</span> <span class="gold" id="tc2">0</span> OF ${S.regions}</div>`,
        `<div>&gt; WINE ROUTES · TOUR OPERATORS  <span class="gold" id="tc3">0</span> · <span class="gold" id="tc4">0</span></div>`,
        `<div>&gt; HONOURS VERIFIED ............ <span id="tb3">${bar(0)}</span> <span class="gold" id="tc5">0</span> · <span id="tc6">0</span> UNDER REVIEW</div>`,
        `<div>&gt; HELD BACK UNTIL THEY MEET THE STANDARD <span class="gold" id="tc7">0</span> RECORDS</div>`,
        `<div class="grey">// EVERY ENTRY TRACEABLE TO ITS SOURCE</div>`,
        `<div class="warn">NOTICE: DETAILS AWAITING A PUBLISHABLE SOURCE ARE HELD BACK</div>`,
        `<div>&nbsp;</div>`,
        `<div>&gt; STATUS <span class="gold">● ATLAS LIVE</span> — <span id="ticker" class="grey"></span><span class="cursor gold">▮</span></div>`
      ];
      body.innerHTML = L.map(l => `<div class="tl">${l}</div>`).join('');
      const rows = [...body.querySelectorAll('.tl')];
      rows.forEach((r, i) => setTimeout(() => r.classList.add('show'), 200 + i*260));
      const animBar = (id, ms, delay) => setTimeout(() => { const el = document.getElementById(id); const t0 = performance.now(); (function f(){ const k = Math.min(1,(performance.now()-t0)/ms); el.innerHTML = bar(k); if(k<1) requestAnimationFrame(f); })(); }, delay);
      animBar('tb1', 1600, 500); setTimeout(() => countTo(document.getElementById('tc1'), S.farms, 1600, n => n), 500);
      animBar('tb2', 1200, 800); setTimeout(() => countTo(document.getElementById('tc2'), S.regions, 1200, n => n), 800);
      setTimeout(() => { countTo(document.getElementById('tc3'), S.routes, 900, n=>n); countTo(document.getElementById('tc4'), S.tours, 900, n=>n); }, 1100);
      setTimeout(() => countTo(document.getElementById('tc7'), S.withheld, 1200, n=>n), 1500);
      animBar('tb3', 1400, 1300); setTimeout(() => { countTo(document.getElementById('tc5'), S.verifiedAwards, 1400, n=>n); countTo(document.getElementById('tc6'), S.pendingClaims, 1400, n=>n); }, 1300);
      // scanning ticker
      let i = 0; const tk = () => { const r = ATLAS.idx[i % ATLAS.idx.length]; const el = document.getElementById('ticker'); if(el) el.textContent = `SCANNING ▸ ${r.name.toUpperCase()} · ${r.farms} PRODUCERS · ${r.awards} HONOURS`; i++; };
      setTimeout(() => { tk(); setInterval(tk, 1700); }, 200 + L.length*260);
    }
    new IntersectionObserver((es, o) => { es.forEach(e => { if(e.isIntersecting){ start(); o.unobserve(e.target); } }); }, { threshold: 0.35 }).observe(document.getElementById('termWindow'));
  })();
  (function(){
  })();


  /* ---- arriving on /region/<key>/: no boot sequence, straight onto the record ---- */
  if(BOOT_REGION){
    clearInterval(plInterval);
    document.getElementById('preloader').classList.add('hide');
    document.getElementById('chrome').classList.add('show');
    startParticles();
    document.getElementById('explore').scrollIntoView();
    openRegion(BOOT_REGION, { fromHistory: true, instant: true });
  }
})();
