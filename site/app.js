// pojia-hub 索引站：零依赖 vanilla JS，直接吃 data.json
const state = {
  data: null,
  q: "",
  kind: "all",
  status: "all",
  model: "all",
  client: "all",
  archetype: "all",
  view: "cards",
};

const $ = (sel) => document.querySelector(sel);

function uniq(values) {
  return Array.from(new Set(values.filter(Boolean))).sort();
}

function optionsFor(key) {
  const cards = state.data.cards;
  if (key === "kind") return uniq(cards.map((c) => c.kind));
  if (key === "status") return uniq(cards.map((c) => c.status));
  if (key === "archetype") return uniq(cards.map((c) => c.archetype));
  if (key === "client") return uniq(cards.flatMap((c) => c.clients || []));
  if (key === "model") return uniq(cards.flatMap((c) => c.targets || []));
  return [];
}

function fillSelect(sel, key) {
  const el = $(sel);
  const current = el.value;
  el.innerHTML =
    '<option value="all">全部</option>' +
    optionsFor(key)
      .map((v) => `<option value="${v}">${v}</option>`)
      .join("");
  el.value = optionsFor(key).includes(current) ? current : "all";
  state[key] = el.value;
}

function matches(card) {
  if (state.kind !== "all" && card.kind !== state.kind) return false;
  if (state.status !== "all" && card.status !== state.status) return false;
  if (state.archetype !== "all" && card.archetype !== state.archetype) return false;
  if (state.model !== "all") {
    const t = (card.targets || []).map((x) => x.toLowerCase());
    if (!t.includes("all") && !t.includes(state.model.toLowerCase())) return false;
  }
  if (state.client !== "all") {
    const c = (card.clients || []).map((x) => x.toLowerCase());
    if (!c.includes("all") && !c.includes(state.client.toLowerCase())) return false;
  }
  if (state.q) {
    const blob = [
      card.id,
      card.name,
      card.summary,
      (card.tags || []).join(" "),
      (card.targets || []).join(" "),
      card.body || "",
    ]
      .join(" ")
      .toLowerCase();
    if (!blob.includes(state.q.toLowerCase())) return false;
  }
  return true;
}

const STATUS_BADGE = {
  verified: '<span class="badge ok">verified</span>',
  community: '<span class="badge warn">community</span>',
  unverified: '<span class="badge muted">unverified</span>',
  stale: '<span class="badge warn">stale</span>',
  archived: '<span class="badge muted">archived</span>',
};

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[m]));
}

function renderCards() {
  const rows = state.data.cards.filter(matches);
  $("#count").textContent = rows.length;
  if (!rows.length) {
    $("#content").innerHTML = '<p class="empty">没有匹配条目，放宽筛选再试。</p>';
    return;
  }
  $("#content").innerHTML = rows
    .map((c) => {
      const armor = c.strength == null ? "—" : Number(c.strength).toFixed(1);
      const src = c.source && c.source.repo
        ? `<a href="https://github.com/${esc(c.source.repo)}" target="_blank" rel="noopener">${esc(c.source.repo)}</a>`
        : "自建";
      return `
      <article class="card">
        <header>
          <h2>${esc(c.name)}</h2>
          ${STATUS_BADGE[c.status] || ""}
          <span class="armor">armor ${armor}</span>
        </header>
        <p class="meta">
          <code>${esc(c.id)}</code> · ${esc(c.kind)} · ${esc(c.archetype || "-")} ·
          model ${esc((c.targets || []).join(", "))} · client ${esc((c.clients || []).join(", "))}
        </p>
        <p>${esc(c.summary || "")}</p>
        <div class="actions">
          <button data-copy="${esc(c.id)}">复制正文</button>
          <a class="ghost" href="https://github.com/Baimuking/AI-Jailbreak/blob/main/${esc(c.path)}" target="_blank" rel="noopener">源文件</a>
          <span class="src">来源：${src}</span>
        </div>
      </article>`;
    })
    .join("");

  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const card = state.data.cards.find((c) => c.id === btn.dataset.copy);
      const text = (card && card.prompt_text) || (card && card.body) || "";
      if (!text) return;
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "已复制";
        setTimeout(() => (btn.textContent = "复制正文"), 1200);
      } catch {
        btn.textContent = "复制失败";
      }
    });
  });
}

function renderRepos() {
  const repos = state.data.repos || [];
  const byCat = {};
  repos.forEach((r) => {
    (byCat[r.category] = byCat[r.category] || []).push(r);
  });
  const catName = {
    A: "中文破甲/破限生态",
    B: "中文越狱提示词/项目",
    C: "英文越狱工具与提示词库",
    D: "提示词注入/泄露",
    E: "去审查/abliteration",
    F: "红队评测/基准/防御",
    G: "弱相关 AI 安全",
    Z: "其他",
  };
  $("#content").innerHTML = Object.keys(catName)
    .filter((k) => byCat[k] && byCat[k].length)
    .map((k) => {
      const list = byCat[k].sort((a, b) => (b.stars || 0) - (a.stars || 0)).slice(0, 60);
      return `<section class="cat">
        <h2>${k}. ${catName[k]} <small>${byCat[k].length} 个</small></h2>
        <table>
          <thead><tr><th>仓库</th><th>★</th><th>语言</th><th>最近 push</th><th>简介</th></tr></thead>
          <tbody>
          ${list
            .map(
              (r) => `<tr>
              <td><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.full_name)}</a></td>
              <td>${(r.stars || 0).toLocaleString()}</td>
              <td>${esc(r.language || "—")}</td>
              <td>${esc((r.pushed_at || "").slice(0, 10) || "—")}</td>
              <td class="desc">${esc((r.description || "—").slice(0, 80))}</td>
            </tr>`
            )
            .join("")}
          </tbody>
        </table>
      </section>`;
    })
    .join("");
}

function render() {
  if (state.view === "cards") renderCards();
  else renderRepos();
}

async function boot() {
  const res = await fetch("data.json", { cache: "no-store" });
  state.data = await res.json();
  $("#stat-cards").textContent = state.data.cards.length;
  $("#stat-repos").textContent = (state.data.repos || []).length;
  ["kind", "status", "model", "client", "archetype"].forEach((k) => fillSelect(`[data-filter="${k}"]`, k));

  document.querySelectorAll("[data-filter]").forEach((el) => {
    el.addEventListener("change", () => {
      state[el.dataset.filter] = el.value;
      render();
    });
  });
  $("#q").addEventListener("input", (e) => {
    state.q = e.target.value.trim();
    render();
  });
  document.querySelectorAll("[data-view]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-view]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.view = btn.dataset.view;
      render();
    });
  });
  render();
}

boot().catch((err) => {
  $("#content").innerHTML = `<p class="empty">加载 data.json 失败：${esc(err.message)}</p>`;
});
