/**
 * W-Booru-Injector — ComfyUI Frontend Extension
 * Deep glossy purple theme with water + wind VFX on node canvas.
 * By Lord Winnougan — https://www.patreon.com/c/u5867556
 */

import { app } from "../../scripts/app.js";

const P = {
  bg:"#0a0612", surface:"#110820", border:"#3b1f6e", borderGlow:"#7c3aed",
  accent:"#c084fc", accentBrt:"#e9d5ff", accentDim:"#6d28d9", accentDeep:"#4c1d95",
  glow:"rgba(192,132,252,0.22)", glowStrong:"rgba(192,132,252,0.45)",
  text:"#ede9fe", textMuted:"#7c3aed",
  water:"#67e8f9", wind:"#a78bfa",
  success:"#86efac", error:"#f87171",
  tag_artist:"#f9a8d4", tag_character:"#93c5fd", tag_copyright:"#fcd34d",
  tag_general:"#a3e635", tag_meta:"#c4b5fd",
};

// ── Styles ───────────────────────────────────────────────────────────────────
(function injectStyles(){
  if(document.getElementById("wbooru-styles"))return;
  const s=document.createElement("style"); s.id="wbooru-styles";
  s.textContent=`
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Cinzel:wght@600&display=swap');
    .wbooru-wrap{font-family:'Space Mono',monospace;position:relative;background:${P.bg};border-radius:0 0 8px 8px;}
    .wbooru-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:35%;background:linear-gradient(180deg,rgba(192,132,252,0.07) 0%,transparent 100%);pointer-events:none;border-radius:0 0 8px 8px;}
    .wbooru-header{display:flex;align-items:center;gap:8px;padding:8px 12px 6px;background:linear-gradient(90deg,${P.accentDeep}44,${P.accentDim}22,transparent);border-bottom:1px solid ${P.border};}
    .wbooru-title{font-family:'Cinzel',serif;font-size:12px;font-weight:600;letter-spacing:0.15em;color:${P.accentBrt};text-shadow:0 0 12px ${P.accent};}
    .wbooru-patreon{margin-left:auto;font-size:9px;color:${P.textMuted};text-decoration:none;letter-spacing:0.06em;transition:color 0.2s;}
    .wbooru-patreon:hover{color:${P.accent};}
    .wbooru-source-badge{font-size:9px;padding:1px 7px;border-radius:10px;background:${P.accentDeep};color:${P.accentBrt};border:1px solid ${P.borderGlow};letter-spacing:0.06em;}
    .wbooru-btn{display:flex;align-items:center;justify-content:center;gap:7px;width:calc(100% - 16px);margin:8px 8px 4px;padding:8px 14px;border-radius:8px;border:1px solid ${P.borderGlow};background:linear-gradient(135deg,${P.accentDeep}88 0%,${P.accentDim}44 50%,${P.accentDeep}22 100%);box-shadow:0 0 0 1px ${P.accentDeep}44,inset 0 1px 0 rgba(255,255,255,0.07),0 4px 24px ${P.glow};color:${P.accentBrt};font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:0.12em;cursor:pointer;transition:all 0.25s ease;position:relative;overflow:hidden;}
    .wbooru-btn::after{content:'';position:absolute;top:0;left:0;right:0;height:50%;background:linear-gradient(180deg,rgba(255,255,255,0.09) 0%,transparent 100%);border-radius:8px 8px 0 0;pointer-events:none;}
    .wbooru-btn:hover{border-color:${P.accent};box-shadow:0 0 0 1px ${P.accentDim},inset 0 1px 0 rgba(255,255,255,0.12),0 0 28px ${P.glowStrong},0 8px 32px ${P.glow};color:#fff;transform:translateY(-1px);}
    .wbooru-btn:active{transform:scale(0.98) translateY(0);}
    .wbooru-btn.loading{opacity:0.6;pointer-events:none;}
    .wbooru-spinner{width:11px;height:11px;border:2px solid ${P.accentDim};border-top-color:${P.accentBrt};border-radius:50%;animation:wbooru-spin 0.65s linear infinite;}
    @keyframes wbooru-spin{to{transform:rotate(360deg);}}
    .wbooru-preview{margin:4px 8px;border:1px solid ${P.border};border-radius:7px;background:${P.surface};overflow:hidden;box-shadow:inset 0 0 20px ${P.glow};}
    .wbooru-preview-hd{display:flex;align-items:center;justify-content:space-between;padding:4px 9px;background:linear-gradient(90deg,${P.accentDeep}33,transparent);border-bottom:1px solid ${P.border};}
    .wbooru-preview-lbl{font-size:9px;letter-spacing:0.1em;text-transform:uppercase;color:${P.textMuted};}
    .wbooru-preview-count{font-size:9px;color:${P.textMuted};}
    .wbooru-preview-body{padding:6px 8px;min-height:30px;max-height:120px;overflow-y:auto;display:flex;flex-wrap:wrap;gap:4px;scrollbar-width:thin;scrollbar-color:${P.border} transparent;}
    .wbooru-tag{display:inline-flex;align-items:center;padding:2px 7px;border-radius:5px;font-size:10px;line-height:1.4;opacity:0;transform:translateY(5px) scale(0.95);animation:wbooru-tag-in 0.22s ease forwards;}
    @keyframes wbooru-tag-in{to{opacity:1;transform:translateY(0) scale(1);}}
    .wbooru-tag.artist{background:rgba(249,168,212,0.10);color:${P.tag_artist};border:1px solid rgba(249,168,212,0.22);}
    .wbooru-tag.character{background:rgba(147,197,253,0.10);color:${P.tag_character};border:1px solid rgba(147,197,253,0.22);}
    .wbooru-tag.copyright{background:rgba(252,211,77,0.10);color:${P.tag_copyright};border:1px solid rgba(252,211,77,0.22);}
    .wbooru-tag.general{background:rgba(163,230,53,0.07);color:${P.tag_general};border:1px solid rgba(163,230,53,0.18);}
    .wbooru-tag.quality{background:rgba(192,132,252,0.12);color:${P.accent};border:1px solid rgba(192,132,252,0.25);}
    .wbooru-tag.meta{background:rgba(196,181,253,0.08);color:${P.tag_meta};border:1px solid rgba(196,181,253,0.2);}
    .wbooru-prompt-wrap{margin:4px 8px;border:1px solid ${P.border};border-radius:7px;background:${P.surface};overflow:hidden;}
    .wbooru-prompt-box{width:100%;box-sizing:border-box;background:transparent;border:none;color:${P.text};font-family:'Space Mono',monospace;font-size:10px;line-height:1.5;padding:6px 9px;resize:vertical;outline:none;scrollbar-width:thin;scrollbar-color:${P.border} transparent;}
    .wbooru-copy-btn{background:none;border:1px solid ${P.border};border-radius:4px;color:${P.textMuted};font-family:'Space Mono',monospace;font-size:9px;padding:1px 6px;cursor:pointer;transition:color 0.2s,border-color 0.2s,box-shadow 0.2s;}
    .wbooru-copy-btn:hover{color:${P.accent};border-color:${P.accent};box-shadow:0 0 8px ${P.glow};}
    .wbooru-legend{display:flex;flex-wrap:wrap;gap:6px;padding:5px 10px;}
    .wbooru-legend-item{display:flex;align-items:center;gap:3px;font-size:9px;color:${P.textMuted};}
    .wbooru-legend-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;}
    .wbooru-status{padding:3px 11px 5px;font-size:10px;border-top:1px solid ${P.border};min-height:20px;transition:color 0.3s;}
    .wbooru-status.ok{color:${P.success};}.wbooru-status.err{color:${P.error};}.wbooru-status.idle{color:${P.textMuted};}
    @keyframes wbooru-ripple{0%{transform:scale(0);opacity:0.7;}100%{transform:scale(5);opacity:0;}}
    .wbooru-ripple{position:absolute;border-radius:50%;width:40px;height:40px;background:radial-gradient(circle,rgba(103,232,249,0.35) 0%,transparent 70%);pointer-events:none;animation:wbooru-ripple 1.6s ease-out forwards;z-index:99;}
  `;
  document.head.appendChild(s);
})();

// ── VFX particle state factory ────────────────────────────────────────────────
function makeParticles(w, h) {
  return {
    drops: Array.from({length:20}, () => ({
      x: Math.random()*w, y: Math.random()*h,
      r: 1+Math.random()*2.2,
      vy: 0.4+Math.random()*0.8, vx: (Math.random()-0.5)*0.35,
      life: Math.random(), max: 0.28+Math.random()*0.42,
    })),
    streaks: Array.from({length:11}, () => ({
      x: Math.random()*w, y: Math.random()*h,
      len: 30+Math.random()*60,
      vx: 1.0+Math.random()*1.3, vy: (Math.random()-0.5)*0.25,
      life: Math.random(), max: 0.09+Math.random()*0.18,
    })),
  };
}

// ── Draw VFX particles onto LiteGraph ctx ────────────────────────────────────
function drawParticles(ctx, p, w, h, yOff) {
  ctx.save();
  ctx.beginPath(); ctx.rect(0, yOff, w, h); ctx.clip();

  for (const d of p.drops) {
    d.x += d.vx; d.y += d.vy; d.life += 0.005;
    if (d.life > 1) { d.life=0; d.x=Math.random()*w; d.y=yOff-4; }
    const a = Math.sin(d.life * Math.PI) * d.max;
    if (a < 0.01) continue;
    const g = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r*5);
    g.addColorStop(0, `rgba(103,232,249,${a})`);
    g.addColorStop(1, `rgba(103,232,249,0)`);
    ctx.beginPath(); ctx.arc(d.x, d.y, d.r*5, 0, Math.PI*2);
    ctx.fillStyle = g; ctx.fill();
    ctx.beginPath(); ctx.arc(d.x, d.y, d.r*0.6, 0, Math.PI*2);
    ctx.fillStyle = `rgba(200,240,255,${a*1.4})`; ctx.fill();
  }

  for (const sk of p.streaks) {
    sk.x += sk.vx; sk.y += sk.vy; sk.life += 0.007;
    if (sk.life > 1 || sk.x > w + sk.len) { sk.life=0; sk.x=-sk.len; sk.y=yOff+Math.random()*h; }
    const a = Math.sin(sk.life * Math.PI) * sk.max;
    if (a < 0.01) continue;
    const gw = ctx.createLinearGradient(sk.x-sk.len, sk.y, sk.x, sk.y);
    gw.addColorStop(0, `rgba(167,139,250,0)`);
    gw.addColorStop(0.5, `rgba(167,139,250,${a})`);
    gw.addColorStop(1, `rgba(167,139,250,0)`);
    ctx.beginPath(); ctx.moveTo(sk.x-sk.len, sk.y); ctx.lineTo(sk.x, sk.y + sk.vy*8);
    ctx.strokeStyle = gw; ctx.lineWidth = 0.9; ctx.stroke();
  }
  ctx.restore();
}

// ── Draw purple glowing border ────────────────────────────────────────────────
function drawBorder(ctx, node) {
  const w = node.size[0];
  const h = node.size[1] + LiteGraph.NODE_TITLE_HEIGHT;
  const yOff = -LiteGraph.NODE_TITLE_HEIGHT;
  const t = Date.now() / 1000;
  const pulse  = 0.5 + 0.5 * Math.sin(t * (Math.PI*2 / 2.2));
  const pulse2 = 0.5 + 0.5 * Math.sin(t * (Math.PI*2 / 0.65) + 1.2);

  ctx.save();

  // Deep outer glow
  ctx.shadowColor="#4c1d95"; ctx.shadowBlur=30+pulse*20;
  ctx.strokeStyle="#4c1d95"; ctx.lineWidth=2; ctx.globalAlpha=0.2+pulse*0.12;
  ctx.beginPath(); ctx.roundRect(-3, yOff-3, w+6, h+6, 10); ctx.stroke();

  // Main purple border
  ctx.shadowColor=P.accentDim; ctx.shadowBlur=16+pulse*18;
  ctx.strokeStyle=P.accentDim; ctx.lineWidth=2.5; ctx.globalAlpha=0.7+pulse*0.22;
  ctx.beginPath(); ctx.roundRect(0, yOff, w, h, 8); ctx.stroke();

  // Bright inner rim
  ctx.shadowColor=P.accent; ctx.shadowBlur=7+pulse2*12;
  ctx.strokeStyle=P.accent; ctx.lineWidth=1; ctx.globalAlpha=0.3+pulse2*0.45;
  ctx.beginPath(); ctx.roundRect(1.5, yOff+1.5, w-3, h-3, 7); ctx.stroke();

  // Corner sparkles
  ctx.shadowColor=P.accentBrt; ctx.shadowBlur=8; ctx.globalAlpha=0.45+pulse*0.5;
  ctx.fillStyle=P.accentBrt;
  const dr = 1.8+pulse*1.8;
  for (const [cx,cy] of [[0,yOff],[w,yOff],[0,yOff+h],[w,yOff+h]]) {
    ctx.beginPath(); ctx.arc(cx, cy, dr, 0, Math.PI*2); ctx.fill();
  }

  // Water-shimmer sweep line
  ctx.shadowBlur=0; ctx.globalAlpha=0.15+pulse2*0.22;
  const sh = ctx.createLinearGradient(0, yOff+2, w, yOff+2);
  sh.addColorStop(0,"transparent"); sh.addColorStop(0.3,P.water);
  sh.addColorStop(0.7,P.accent); sh.addColorStop(1,"transparent");
  ctx.strokeStyle=sh; ctx.lineWidth=1.3;
  ctx.beginPath(); ctx.moveTo(0,yOff+2); ctx.lineTo(w,yOff+2); ctx.stroke();

  ctx.restore();
}

// ── Water ripple on DOM click ─────────────────────────────────────────────────
function spawnRipple(container, x, y) {
  const el = document.createElement("div");
  el.className = "wbooru-ripple";
  el.style.left = (x - 20) + "px";
  el.style.top  = (y - 20) + "px";
  container.style.position = "relative";
  container.appendChild(el);
  setTimeout(() => el.remove(), 1700);
}

// ── Extension ─────────────────────────────────────────────────────────────────
app.registerExtension({
  name: "WBooru.Injector",

  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (!["WDanbooru_Injector","WDanbooru_NegativePreset","WDanbooru_Grabber"].includes(nodeData.name)) return;

    // ── Purple border + VFX on the LiteGraph canvas ──────────────────────────
    const origCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
      origCreated?.apply(this, arguments);
      this.color   = "#0a0612";
      this.bgcolor = "#110820";
      // Init VFX particles lazily on first draw
      this._wbooru_particles = null;
    };

    const origFg = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function(ctx) {
      origFg?.call(this, ctx);
      if (this.flags?.collapsed) return;

      const w    = this.size[0];
      const h    = this.size[1] + LiteGraph.NODE_TITLE_HEIGHT;
      const yOff = -LiteGraph.NODE_TITLE_HEIGHT;

      // Init particles once we know dimensions
      if (!this._wbooru_particles) {
        this._wbooru_particles = makeParticles(w, h);
      }

      // Draw particles then border (border on top)
      drawParticles(ctx, this._wbooru_particles, w, h, yOff);
      drawBorder(ctx, this);

      // Keep animating
      app.graph.setDirtyCanvas(true, false);
    };

    // ── DOM widget only for Injector node ────────────────────────────────────
    if (nodeData.name !== "WDanbooru_Injector") return;

    const origNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
      origNodeCreated?.apply(this, arguments);
      const node = this;
      node.size = [360, node.size?.[1] ?? 480];

      const outer = document.createElement("div");
      outer.className = "wbooru-wrap";

      outer.innerHTML = `
        <div class="wbooru-header">
          <span style="font-size:16px">🌸</span>
          <span class="wbooru-title">W-Booru Injector</span>
          <span class="wbooru-source-badge" id="wbooru-src-badge">gelbooru</span>
          <a class="wbooru-patreon" href="https://www.patreon.com/c/u5867556" target="_blank">♥ Patreon</a>
        </div>
        <button class="wbooru-btn" id="wbooru-fetch-btn">
          <span class="btn-icon">⬇</span><span>FETCH &amp; PREVIEW TAGS</span>
        </button>
        <div class="wbooru-preview" id="wbooru-preview" style="display:none">
          <div class="wbooru-preview-hd">
            <span class="wbooru-preview-lbl">Tag Preview</span>
            <span class="wbooru-preview-count" id="wbooru-tag-count">0 tags</span>
          </div>
          <div class="wbooru-preview-body" id="wbooru-preview-body"></div>
        </div>
        <div class="wbooru-prompt-wrap" id="wbooru-prompt-wrap" style="display:none">
          <div class="wbooru-preview-hd">
            <span class="wbooru-preview-lbl">Full Prompt Preview</span>
            <button class="wbooru-copy-btn" id="wbooru-copy-btn">⎘ copy</button>
          </div>
          <textarea class="wbooru-prompt-box" id="wbooru-prompt-box" readonly rows="4" placeholder="Prompt appears here after fetch…"></textarea>
        </div>
        <div class="wbooru-legend">
          <div class="wbooru-legend-item"><div class="wbooru-legend-dot" style="background:${P.tag_artist}"></div>artist</div>
          <div class="wbooru-legend-item"><div class="wbooru-legend-dot" style="background:${P.tag_character}"></div>character</div>
          <div class="wbooru-legend-item"><div class="wbooru-legend-dot" style="background:${P.tag_copyright}"></div>copyright</div>
          <div class="wbooru-legend-item"><div class="wbooru-legend-dot" style="background:${P.tag_general}"></div>general</div>
          <div class="wbooru-legend-item"><div class="wbooru-legend-dot" style="background:${P.accent}"></div>quality</div>
        </div>
        <div class="wbooru-status idle" id="wbooru-status">Ready — enter a post ID or URL and click Fetch</div>
      `;

      node.addDOMWidget("wbooru_ui", "wbooru_ui", outer);

      // Ripple on click
      outer.addEventListener("click", e => {
        const r = outer.getBoundingClientRect();
        spawnRipple(outer, e.clientX - r.left, e.clientY - r.top);
      });

      // ── Widget logic ──────────────────────────────────────────────────────
      const fetchBtn    = outer.querySelector("#wbooru-fetch-btn");
      const statusEl    = outer.querySelector("#wbooru-status");
      const previewEl   = outer.querySelector("#wbooru-preview");
      const previewBody = outer.querySelector("#wbooru-preview-body");
      const tagCount    = outer.querySelector("#wbooru-tag-count");
      const srcBadge    = outer.querySelector("#wbooru-src-badge");
      const promptWrap  = outer.querySelector("#wbooru-prompt-wrap");
      const promptBox   = outer.querySelector("#wbooru-prompt-box");
      const copyBtn     = outer.querySelector("#wbooru-copy-btn");

      const gw = name => node.widgets?.find(w => w.name === name)?.value ?? null;
      const setStatus = (msg, type="idle") => { statusEl.textContent=msg; statusEl.className=`wbooru-status ${type}`; };
      const pill = (text, cat, delay=0) => { const el=document.createElement("span"); el.className=`wbooru-tag ${cat}`; el.textContent=text; el.style.animationDelay=`${delay}ms`; return el; };
      const buildPrompt = (parts, mode, base) => { const inj=parts.filter(Boolean).join(", "); base=(base??"").trim(); if(mode==="replace"||!base)return inj; if(mode==="append")return base+(inj?", "+inj:""); return inj+(base?", "+base:""); };
      const parseId = raw => { raw=(raw??"").trim(); let m; if((m=raw.match(/\/posts\/(\d+)/)))return parseInt(m[1],10); if((m=raw.match(/post\/show\/(\d+)/)))return parseInt(m[1],10); if((m=raw.match(/[?&]id=(\d+)/)))return parseInt(m[1],10); if(/^\d+$/.test(raw))return parseInt(raw,10); return 0; };

      copyBtn.addEventListener("click", () => {
        if (!promptBox.value) return;
        navigator.clipboard.writeText(promptBox.value).then(() => {
          copyBtn.textContent="✓ copied"; setTimeout(()=>{ copyBtn.textContent="⎘ copy"; },1500);
        });
      });

      async function fetchAndPreview() {
        const source   = gw("source") ?? "gelbooru";
        const postId   = parseId(gw("post_id") ?? "");
        const manual   = gw("manual_tags") ?? "";

        srcBadge.textContent = source;
        previewBody.innerHTML = ""; previewEl.style.display="none"; promptWrap.style.display="none"; promptBox.value="";

        if (source === "manual") {
          if (!manual.trim()) { setStatus("Manual mode: no tags entered.","err"); return; }
          const tags = manual.split(/[,\n]+/).map(t=>t.trim()).filter(Boolean);
          const pts=[]; const q=gw("quality_prefix")||"";
          if(q)pts.push(...q.split(",").map(s=>s.trim()).filter(Boolean));
          const sft=gw("safety_tag")??"none"; if(sft&&sft!=="none")pts.push(sft);
          const yr=gw("year_tag")??"none"; if(yr&&yr!=="none")pts.push("year "+yr);
          pts.push(...tags);
          tags.forEach((t,i)=>previewBody.appendChild(pill(t,"general",i*12)));
          tagCount.textContent=`${tags.length} tags`; previewEl.style.display="block";
          promptBox.value=buildPrompt(pts,gw("inject_mode")??"prepend",gw("positive_prompt")??"");
          promptWrap.style.display="block"; setStatus(`✓ ${tags.length} manual tags ready`,"ok"); return;
        }

        if (postId===0) { setStatus("Set a valid post ID or URL first.","err"); return; }

        fetchBtn.classList.add("loading");
        fetchBtn.querySelector(".btn-icon").outerHTML='<span class="wbooru-spinner"></span>';
        setStatus(`Fetching ${source} post #${postId}…`,"idle");

        try {
          let artistTags=[], charTags=[], copyrightTags=[], generalTags=[];

          if (source==="gelbooru") {
            const uid=(gw("gelbooru_user_id")??"").split("=").pop().trim();
            const key=(gw("gelbooru_api_key")??"").split("=").pop().trim();
            if(!uid||!key) throw new Error("Gelbooru requires API credentials. Fill in gelbooru_user_id and gelbooru_api_key.");
            const resp=await fetch(`https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=${postId}&user_id=${uid}&api_key=${key}`);
            if(resp.status===401)throw new Error("Gelbooru rejected credentials (401).");
            if(!resp.ok)throw new Error(`Gelbooru error ${resp.status}`);
            const gd=await resp.json(); let posts=Array.isArray(gd)?gd:(gd?.post??[]); if(!Array.isArray(posts))posts=[posts];
            const post=posts[0]; if(!post)throw new Error(`No Gelbooru post for ID ${postId}`);
            generalTags=(post.tags||"").split(" ").filter(Boolean);

          } else if (source==="e621") {
            const eu=(gw("e621_username")??"").trim(); const ek=(gw("e621_api_key")??"").trim();
            const headers={"User-Agent":eu?`WBooru-Injector/2.0 (by ${eu})`:"WBooru-Injector/2.0 (ComfyUI)"};
            const params=eu&&ek?`?login=${eu}&api_key=${ek}`:"";
            const resp=await fetch(`https://e621.net/posts/${postId}.json${params}`,{headers});
            if(resp.status===401)throw new Error("e621 auth failed. Leave both fields empty for anonymous, or fill both username AND api_key.");
            if(!resp.ok)throw new Error(`e621 error ${resp.status}`);
            const ed=await resp.json(); const tags=ed?.post?.tags??{};
            artistTags=(tags.artist??[]).map(t=>t.replace(/_/g," "));
            charTags=(tags.character??[]).map(t=>t.replace(/_/g," "));
            copyrightTags=(tags.copyright??[]).map(t=>t.replace(/_/g," "));
            generalTags=[...(tags.species??[]),...(tags.general??[]),...(tags.meta??[])].map(t=>t.replace(/_/g," "));

          } else if (source==="danbooru") {
            const du=(gw("danbooru_username")??"").trim(); const dk=(gw("danbooru_api_key")??"").trim();
            const params=du&&dk?`?login=${du}&api_key=${dk}`:"";
            const resp=await fetch(`https://danbooru.donmai.us/posts/${postId}.json${params}`);
            if(resp.status===401)throw new Error("Danbooru rejected credentials (401).");
            if(!resp.ok)throw new Error(`Danbooru error ${resp.status}`);
            const dd=await resp.json();
            const artistStr=dd.tag_string_artist||""; const charStr=dd.tag_string_character||"";
            const copyStr=dd.tag_string_copyright||""; const allStr=dd.tag_string||"";
            const skip=new Set([...artistStr.split(" "),...charStr.split(" "),...copyStr.split(" ")].filter(Boolean));
            artistTags=artistStr.split(" ").filter(Boolean).map(t=>t.replace(/_/g," "));
            charTags=charStr.split(" ").filter(Boolean).map(t=>t.replace(/_/g," "));
            copyrightTags=copyStr.split(" ").filter(Boolean).map(t=>t.replace(/_/g," "));
            generalTags=allStr.split(" ").filter(t=>t&&!skip.has(t)).map(t=>t.replace(/_/g," "));

          } else if (source==="konachan.net"||source==="konachan.com") {
            const domain=source==="konachan.net"?"konachan.net":"konachan.com";
            const resp=await fetch(`https://${domain}/post.json?tags=id:${postId}`);
            if(!resp.ok)throw new Error(`Konachan error ${resp.status}`);
            const kd=await resp.json(); if(!kd?.length)throw new Error(`No Konachan post for ID ${postId}`);
            generalTags=(kd[0].tags||"").split(" ").filter(Boolean).map(t=>t.replace(/_/g," "));
            if(kd[0].author)artistTags=[kd[0].author.replace(/_/g," ")];

          } else if (source==="yande.re") {
            const resp=await fetch(`https://yande.re/post.json?tags=id:${postId}`);
            if(!resp.ok)throw new Error(`Yande.re error ${resp.status}`);
            const yd=await resp.json(); if(!yd?.length)throw new Error(`No Yande.re post for ID ${postId}`);
            generalTags=(yd[0].tags||"").split(" ").filter(Boolean).map(t=>t.replace(/_/g," "));
            if(yd[0].author)artistTags=[yd[0].author.replace(/_/g," ")];

          } else if (source==="lolibooru") {
            const resp=await fetch(`https://lolibooru.moe/post.json?tags=id:${postId}`);
            if(!resp.ok)throw new Error(`Lolibooru error ${resp.status}`);
            const ld=await resp.json(); if(!ld?.length)throw new Error(`No Lolibooru post for ID ${postId}`);
            generalTags=(ld[0].tags||"").split(" ").filter(Boolean).map(t=>t.replace(/_/g," "));
            if(ld[0].author)artistTags=[ld[0].author.replace(/_/g," ")];

          } else if (["safebooru","rule34","hypnohub","atfbooru","xbooru"].includes(source)) {
            const dapiMap={
              safebooru:"https://safebooru.org/index.php",
              rule34:"https://api.rule34.xxx/index.php",
              hypnohub:"https://hypnohub.net/index.php",
              atfbooru:"https://booru.allthefallen.moe/index.php",
              xbooru:"https://xbooru.com/index.php",
            };
            const base=dapiMap[source];
            const resp=await fetch(`${base}?page=dapi&s=post&q=index&json=1&id=${postId}`);
            if(!resp.ok)throw new Error(`${source} error ${resp.status}`);
            const rd=await resp.json();
            let posts=Array.isArray(rd)?rd:(rd?.post??[]); if(!Array.isArray(posts))posts=[posts];
            const post=posts[0]; if(!post)throw new Error(`No ${source} post for ID ${postId}`);
            generalTags=(post.tags||"").split(" ").filter(Boolean).map(t=>t.replace(/_/g," "));
          }

          let total=0; const maxG=parseInt(gw("max_general_tags")??40,10); const pts=[];
          const q=gw("quality_prefix")||"";
          if(q)q.split(",").forEach(s=>{if(!s.trim())return; previewBody.appendChild(pill(s.trim(),"quality",total++*10)); pts.push(s.trim());});
          const yr=gw("year_tag")??"none"; if(yr&&yr!=="none"){previewBody.appendChild(pill("year "+yr,"meta",total++*10));pts.push("year "+yr);}
          const sft=gw("safety_tag")??"none"; if(sft&&sft!=="none"){previewBody.appendChild(pill(sft,"meta",total++*10));pts.push(sft);}
          const ct=(gw("count_tag")??"").trim(); if(ct)pts.push(ct);
          if(gw("include_character")!==false)charTags.forEach(t=>{previewBody.appendChild(pill(t,"character",total++*10));pts.push(t);});
          if(gw("include_copyright")!==false)copyrightTags.forEach(t=>{previewBody.appendChild(pill(t,"copyright",total++*10));pts.push(t);});
          if(gw("include_artist")!==false)artistTags.forEach(t=>{const l="@"+t;previewBody.appendChild(pill(l,"artist",total++*10));pts.push(l);});
          if(gw("include_general")!==false)generalTags.slice(0,maxG).forEach(t=>{previewBody.appendChild(pill(t,"general",total++*10));pts.push(t);});

          tagCount.textContent=`${total} tags`; previewEl.style.display="block";
          promptBox.value=buildPrompt(pts,gw("inject_mode")??"prepend",gw("positive_prompt")??"");
          promptWrap.style.display="block";
          setStatus(`✓ ${total} tags from ${source} #${postId}`,"ok");
          node.setSize([node.size[0], node.computeSize()[1]]);

        } catch(err) {
          setStatus(`✗ ${err.message}`,"err");
        } finally {
          fetchBtn.classList.remove("loading");
          const sp=fetchBtn.querySelector(".wbooru-spinner"); if(sp)sp.outerHTML='<span class="btn-icon">⬇</span>';
        }
      }

      fetchBtn.addEventListener("click", fetchAndPreview);
      const sw=node.widgets?.find(w=>w.name==="source");
      if(sw){const orig=sw.callback;sw.callback=function(v){orig?.call(this,v);if(srcBadge)srcBadge.textContent=v;};}
    };
  },
});
