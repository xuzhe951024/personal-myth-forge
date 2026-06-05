const form = document.getElementById("myth-form");
const statusLine = document.getElementById("status-line");
const providerBadges = document.getElementById("provider-badges");
const worldStateStrip = document.getElementById("world-state-strip");
const visibleChanges = document.getElementById("visible-changes");
const output = document.getElementById("session-output");
const canvas = document.getElementById("artifact-canvas");
const assetViewer = document.getElementById("asset-viewer");
const ctx = canvas.getContext("2d");

let animationFrame = 0;
let activeSeed = "quiet";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  statusLine.textContent = "Forging...";

  try {
    const response = await fetch("/v1/myth-sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildPayload(new FormData(form))),
    });
    if (!response.ok) {
      throw new Error(`Session failed with HTTP ${response.status}`);
    }
    const session = await response.json();
    renderSession(session);
  } catch (error) {
    statusLine.innerHTML = `<span class="error">${escapeHtml(error.message)}</span>`;
  } finally {
    button.disabled = false;
  }
});

function buildPayload(data) {
  return {
    object_observation: {
      label: requiredText(data, "label"),
      materials: splitMaterials(data.get("materials")),
      source: requiredText(data, "source"),
      visual_notes: optionalText(data, "visual_notes"),
    },
    context_capsule: {
      current_theme: requiredText(data, "current_theme"),
      desired_tone: requiredText(data, "desired_tone"),
      recent_milestone: optionalText(data, "recent_milestone"),
    },
  };
}

function renderSession(session) {
  activeSeed = `${session.session_id}:${session.object_card.label}`;
  startArtifact(activeSeed);
  renderAssetViewer(session.generated_asset);
  renderProviderBadges(session);
  renderWorldState(session.world_resolution);
  renderVisibleChanges(session.world_resolution);
  statusLine.textContent = `${session.status} | ${session.session_id}`;
  output.innerHTML = `
    <article class="result-band">
      <h2>${escapeHtml(session.myth_seed.title)}</h2>
      <p>${escapeHtml(session.myth_seed.personal_resonance)}</p>
    </article>
    <div class="split-grid">
      <article class="result-band">
        <h3>Object Card</h3>
        <p><strong>${escapeHtml(session.object_card.label)}</strong></p>
        <p>${escapeHtml(session.object_card.symbolic_reading)}</p>
        <p class="meta">${escapeHtml(session.object_card.materials.join(", ") || "unknown matter")}</p>
      </article>
      <article class="result-band">
        <h3>Game Asset</h3>
        <p><strong>${escapeHtml(session.generated_asset.provider)}</strong> ${escapeHtml(session.generated_asset.format)}</p>
        <p><a class="asset-link" href="${escapeAttr(uriForDisplay(session.generated_asset.uri))}" target="_blank" rel="noreferrer">${escapeHtml(session.generated_asset.uri)}</a></p>
      </article>
    </div>
    <section class="npc-list" aria-label="NPC reactions">
      ${session.npc_reactions
        .map((reaction) => renderNpc(reaction, session.world_resolution))
        .join("")}
    </section>
    <article class="result-band">
      <h3>Print Candidate</h3>
      <p><strong>${escapeHtml(session.print_candidate.provider)}</strong> ${escapeHtml(session.print_candidate.format)}</p>
      <p>${escapeHtml(session.print_candidate.approval_reason)}</p>
      <p class="meta">${escapeHtml(session.print_candidate.printability_notes.join(" | "))}</p>
    </article>
  `;
}

function renderProviderBadges(session) {
  providerBadges.innerHTML = `
    <span>3D ${escapeHtml(session.generated_asset.provider)}</span>
    <span>NPC ${escapeHtml(session.npc_director)}</span>
    <span>World ${escapeHtml(session.world_resolution.arbitrator)}</span>
  `;
}

function renderWorldState(resolution) {
  worldStateStrip.innerHTML = Object.entries(resolution.world_state_delta)
    .map(
      ([key, value]) => `
        <div>
          <strong>${escapeHtml(value)}</strong>
          <span>${escapeHtml(labelize(key))}</span>
        </div>
      `,
    )
    .join("");
}

function renderVisibleChanges(resolution) {
  visibleChanges.innerHTML = `
    <h2>World Changes</h2>
    <ul>
      ${resolution.visible_changes.map((change) => `<li>${escapeHtml(change)}</li>`).join("")}
    </ul>
  `;
}

function renderNpc(reaction, resolution) {
  const resolvedActions = actionsForNpc(resolution, reaction.npc_id);
  return `
    <article class="npc-card">
      <header>
        <h3>${escapeHtml(reaction.name)}</h3>
        <span class="emotion">${escapeHtml(reaction.emotion)}</span>
      </header>
      <p>${escapeHtml(reaction.interpretation)}</p>
      <ul class="plans action-resolution">
        ${resolvedActions
          .map(
            (action) => `
              <li class="${escapeAttr(action.status)}">
                <span>${escapeHtml(action.status)}</span>
                ${escapeHtml(action.action)}
              </li>
            `,
          )
          .join("")}
      </ul>
      <p class="small">${escapeHtml(reaction.world_change)}</p>
    </article>
  `;
}

function actionsForNpc(resolution, npcId) {
  return [...resolution.accepted_actions, ...resolution.rejected_actions].filter(
    (action) => action.npc_id === npcId,
  );
}

function renderAssetViewer(asset) {
  if (asset.uri.startsWith("http://") || asset.uri.startsWith("https://")) {
    assetViewer.style.display = "block";
    assetViewer.innerHTML = `
      <model-viewer
        src="${escapeAttr(asset.uri)}"
        camera-controls
        auto-rotate
        shadow-intensity="0.8"
        ar
      ></model-viewer>
    `;
    return;
  }
  assetViewer.style.display = "none";
  assetViewer.innerHTML = "";
}

function startArtifact(seed) {
  cancelAnimationFrame(animationFrame);
  const colors = colorsForSeed(seed);

  function frame(time) {
    drawArtifact(time / 1000, colors);
    animationFrame = requestAnimationFrame(frame);
  }

  animationFrame = requestAnimationFrame(frame);
}

function drawArtifact(time, colors) {
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#e8efe9";
  ctx.fillRect(0, 0, width, height);

  ctx.save();
  ctx.translate(width / 2, height / 2 + 18);
  ctx.scale(1 + Math.sin(time) * 0.035, 1);

  ctx.fillStyle = "rgba(28, 27, 34, 0.16)";
  ctx.beginPath();
  ctx.ellipse(0, 132, 148, 18, 0, 0, Math.PI * 2);
  ctx.fill();

  const sway = Math.sin(time * 1.2) * 10;
  ctx.translate(sway, 0);

  ctx.fillStyle = colors.base;
  roundedRect(-34, -20, 68, 150, 16);
  ctx.fill();

  ctx.fillStyle = colors.accent;
  ctx.beginPath();
  ctx.moveTo(0, -142);
  ctx.lineTo(78, -46);
  ctx.lineTo(0, 22);
  ctx.lineTo(-78, -46);
  ctx.closePath();
  ctx.fill();

  ctx.strokeStyle = colors.line;
  ctx.lineWidth = 7;
  ctx.beginPath();
  ctx.moveTo(0, -112);
  ctx.lineTo(0, 95);
  ctx.moveTo(-44, -44);
  ctx.lineTo(44, -44);
  ctx.moveTo(-24, 58);
  ctx.lineTo(24, 58);
  ctx.stroke();

  ctx.fillStyle = colors.spark;
  ctx.beginPath();
  ctx.moveTo(0, -172);
  ctx.lineTo(16, -136);
  ctx.lineTo(0, -120);
  ctx.lineTo(-16, -136);
  ctx.closePath();
  ctx.fill();

  ctx.restore();
}

function roundedRect(x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.arcTo(x + width, y, x + width, y + height, radius);
  ctx.arcTo(x + width, y + height, x, y + height, radius);
  ctx.arcTo(x, y + height, x, y, radius);
  ctx.arcTo(x, y, x + width, y, radius);
  ctx.closePath();
}

function colorsForSeed(seed) {
  const hash = [...seed].reduce((value, char) => value + char.charCodeAt(0), 0);
  const palettes = [
    { base: "#176b5f", accent: "#b8872f", line: "#f8f3dd", spark: "#b85143" },
    { base: "#355c8a", accent: "#b85143", line: "#f6ead8", spark: "#176b5f" },
    { base: "#5d6638", accent: "#355c8a", line: "#f8f3dd", spark: "#b8872f" },
  ];
  return palettes[hash % palettes.length];
}

function splitMaterials(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function requiredText(data, key) {
  return String(data.get(key) || "").trim();
}

function optionalText(data, key) {
  const value = requiredText(data, key);
  return value || null;
}

function labelize(value) {
  return String(value).replaceAll("_", " ");
}

function uriForDisplay(uri) {
  if (uri.startsWith("http://") || uri.startsWith("https://")) {
    return uri;
  }
  return "#";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

startArtifact(activeSeed);
