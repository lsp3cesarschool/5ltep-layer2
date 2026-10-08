// 5L-TEP Layer 2 dashboard. Reads data/layer2.json and, on demand, data/rules/<id>.json (both written
// by `python main.py run`). No library, no build step. Every text from the data is inserted as text,
// never as HTML. The visitor's order of the rule cards is kept in localStorage and changes nothing
// in the evaluation.

const I18N = {
  en: {
    back: "← Back to the repository", eyebrow: "5L-TEP · Layer 2 · Semantic Policies", loading: "Loading…",
    title: "Semantic policies over open data", run: "Run now ↗", rules_btn: "Rule files ↗", manifest_btn: "Manifest ↗",
    intro: "Each rule crosses data published on CKAN open data portals. Every week this repository downloads each resource once, records whether each portal answered and what it served, and counts, for every rule, the records that deserve a second look. A signal is something to review, never a verdict on the data; no value from the portals is published here, only counts and record numbers.",
    subtitle: "Last run {at} · {env}", env_actions: "GitHub Actions", env_local: "local test run: not a published result",
    no_data: "No run has been published yet.",
    t_rules: "Rules evaluated", t_rules_note: "{n} not evaluated in this run", t_rules_all: "all rules evaluated",
    t_signals: "Signals to review", t_signals_note: "in {n} rule(s)",
    t_sources: "Sources available", t_sources_note: "{n} failed", t_sources_all: "every portal answered",
    t_records: "Records checked", t_records_note: "across {n} source file(s)",
    rules_h: "Rules", order: "Order", o_custom: "My order", o_signals: "Most signals first", o_title: "Title",
    o_file: "Folder and file", group: "group by folder", search_rules: "Search rules",
    order_note: "Use ↑ ↓ to arrange the cards; your order is kept in this browser only and changes nothing in the evaluation.",
    up: "Move up", down: "Move down", root_folder: "(rules/)",
    datasets: "Datasets", justification: "Justification", exceptions: "Exceptions", examples: "Examples", history: "History",
    no_exceptions: "None recorded.", expected: "Expected",
    signals_at: "{n} signal(s) on {d}", of_records: "of {n} records", not_evaluated: "✕ Not evaluated in this run",
    no_signal: "✓ no signal on {d}",
    see_list: "see list", hide_list: "hide list", show_all: "show all {n}", download: "Download JSON of this list",
    download_all: "Full JSON of the rule", numbering: "Record numbers per file of the resource (1 = first line after the header), valid for the bytes with SHA-256 {sha}.",
    loading_list: "Loading…", list_error: "Could not load the list.",
    out_mismatch: "value differs", out_key_not_found: "key not found", out_missing_value: "no information",
    out_ambiguous_key: "ambiguous key", out_match: "consistent",
    tip_mismatch: "The key was found in the lookup source and the compared value differs.",
    tip_key_not_found: "The key is not in the lookup source.",
    tip_missing_value: "The key or the compared value is empty.",
    tip_ambiguous_key: "The key appears in the lookup source with different values.",
    hist_none: "This is the first run.", h_run: "Run (UTC)", h_env: "Where", h_sources: "Sources ok", h_signals: "signals",
    sources_h: "Source health",
    sources_note: "Each CKAN resource is downloaded once per run, however many rules use it. A rule whose source failed is not evaluated in that run: there is no partial result and no reuse of an earlier download.",
    s_resource: "Resource", s_status: "Status", s_portal: "Portal answer", s_download: "Download", s_modified: "Modified (CKAN)",
    s_sha: "SHA-256", s_used: "Used by",
    st_ok: "✓ available", st_portal_unreachable: "✕ portal did not answer", st_resource_not_found: "✕ resource not found",
    st_resource_ambiguous: "✕ more than one resource matches", st_download_failed: "✕ download failed",
    history_h: "History", history_note: "Signals per rule in each run, and the runs in which a source failed.",
    prov_h: "Provenance of this result",
    prov_note: "What this run evaluated: the engine version, each rule file and the bytes of each source, identified by SHA-256. Record numbers are valid only for those bytes.",
    engine_h: "Run", hashes_h: "Rules and sources",
    k_env: "where", k_started: "started (UTC)", k_finished: "finished (UTC)", k_commit: "engine commit", k_dirty: "uncommitted engine changes",
    k_python: "Python", k_duckdb: "DuckDB", k_run: "Actions run", yes: "yes", no: "no",
    hx_kind: "Kind", hx_name: "Name", hx_sha: "SHA-256", hx_rule: "rule", hx_source: "source",
    datasets_h: "Datasets crossed", d_dataset: "Dataset", d_org: "Publisher", d_license: "License", d_rules: "Rules",
    reason: "Reason",
    footer: "Layer 2 of 5L-TEP (Layers 1, 3 and 4 are separate repositories). Data:",
  },
  pt: {
    back: "← Voltar ao repositório", eyebrow: "5L-TEP · Camada 2 · Políticas Semânticas", loading: "Carregando…",
    title: "Políticas semânticas sobre dados abertos", run: "Rodar agora ↗", rules_btn: "Arquivos de regras ↗",
    manifest_btn: "Manifesto ↗",
    intro: "Cada regra cruza dados publicados em portais de dados abertos CKAN. Toda semana este repositório baixa cada recurso uma vez, registra se cada portal respondeu e o que entregou, e conta, para cada regra, os registros que merecem um segundo olhar. Um sinal é algo a revisar, nunca um veredito sobre os dados; nenhum valor dos portais é publicado aqui, só contagens e números de registro.",
    subtitle: "Última rodada {at} · {env}", env_actions: "GitHub Actions", env_local: "ensaio local: não é resultado publicado",
    no_data: "Nenhuma rodada foi publicada ainda.",
    t_rules: "Regras avaliadas", t_rules_note: "{n} não avaliada(s) nesta rodada", t_rules_all: "todas as regras avaliadas",
    t_signals: "Sinais a revisar", t_signals_note: "em {n} regra(s)",
    t_sources: "Fontes disponíveis", t_sources_note: "{n} com falha", t_sources_all: "todos os portais responderam",
    t_records: "Registros conferidos", t_records_note: "em {n} arquivo(s) das fontes",
    rules_h: "Regras", order: "Ordem", o_custom: "Minha ordem", o_signals: "Mais sinais primeiro", o_title: "Título",
    o_file: "Pasta e arquivo", group: "agrupar por pasta", search_rules: "Buscar regras",
    order_note: "Use ↑ ↓ para arrumar os cartões; a ordem fica só neste navegador e não muda nada na avaliação.",
    up: "Subir", down: "Descer", root_folder: "(rules/)",
    datasets: "Datasets", justification: "Justificativa", exceptions: "Exceções", examples: "Exemplos", history: "Histórico",
    no_exceptions: "Nenhuma registrada.", expected: "Esperado",
    signals_at: "{n} sinal(is) em {d}", of_records: "de {n} registros", not_evaluated: "✕ Não avaliada nesta rodada",
    no_signal: "✓ nenhum sinal em {d}",
    see_list: "ver lista", hide_list: "ocultar lista", show_all: "mostrar todos os {n}", download: "Baixar JSON desta lista",
    download_all: "JSON completo da regra", numbering: "Números de registro por arquivo do recurso (1 = primeira linha após o cabeçalho), válidos para os bytes com SHA-256 {sha}.",
    loading_list: "Carregando…", list_error: "Não foi possível carregar a lista.",
    out_mismatch: "valor diverge", out_key_not_found: "chave não encontrada", out_missing_value: "sem informação",
    out_ambiguous_key: "chave ambígua", out_match: "consistente",
    tip_mismatch: "A chave foi encontrada na fonte de consulta e o valor comparado é diferente.",
    tip_key_not_found: "A chave não está na fonte de consulta.",
    tip_missing_value: "A chave ou o valor comparado está vazio.",
    tip_ambiguous_key: "A chave aparece na fonte de consulta com valores diferentes.",
    hist_none: "Esta é a primeira rodada.", h_run: "Rodada (UTC)", h_env: "Onde", h_sources: "Fontes ok", h_signals: "sinais",
    sources_h: "Saúde das fontes",
    sources_note: "Cada recurso CKAN é baixado uma vez por rodada, não importa quantas regras o usem. Regra com fonte em falha não é avaliada naquela rodada: não há resultado parcial nem reaproveitamento de download anterior.",
    s_resource: "Recurso", s_status: "Estado", s_portal: "Resposta do portal", s_download: "Download", s_modified: "Modificado (CKAN)",
    s_sha: "SHA-256", s_used: "Usado por",
    st_ok: "✓ disponível", st_portal_unreachable: "✕ portal não respondeu", st_resource_not_found: "✕ recurso não encontrado",
    st_resource_ambiguous: "✕ mais de um recurso casa", st_download_failed: "✕ download falhou",
    history_h: "Histórico", history_note: "Sinais por regra em cada rodada, e as rodadas em que alguma fonte falhou.",
    prov_h: "Proveniência deste resultado",
    prov_note: "O que esta rodada avaliou: versão do motor, cada arquivo de regra e os bytes de cada fonte, identificados por SHA-256. Os números de registro valem só para esses bytes.",
    engine_h: "Rodada", hashes_h: "Regras e fontes",
    k_env: "onde", k_started: "início (UTC)", k_finished: "fim (UTC)", k_commit: "commit do motor", k_dirty: "mudanças não commitadas no motor",
    k_python: "Python", k_duckdb: "DuckDB", k_run: "execução no Actions", yes: "sim", no: "não",
    hx_kind: "Tipo", hx_name: "Nome", hx_sha: "SHA-256", hx_rule: "regra", hx_source: "fonte",
    datasets_h: "Datasets cruzados", d_dataset: "Dataset", d_org: "Publicador", d_license: "Licença", d_rules: "Regras",
    reason: "Motivo",
    footer: "Camada 2 do 5L-TEP (as camadas 1, 3 e 4 são repositórios separados). Dados:",
  },
};

const SIGNAL_OUTCOMES = ["mismatch", "key_not_found", "missing_value", "ambiguous_key"];
const LIST_PREVIEW = 300;

// --- small helpers ---------------------------------------------------------------------------
const el = (id) => document.getElementById(id);
function h(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat(Infinity)) if (c !== null && c !== undefined && c !== false) node.append(c instanceof Node ? c : String(c));
  return node;
}
function store(key, value) {
  try {
    if (value === undefined) return JSON.parse(localStorage.getItem(key));
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) { /* storage blocked: the page works without it */ }
  return null;
}

// Language: ?lang= > the visitor's last choice > the browser's language.
const LANG = (() => {
  const q = new URLSearchParams(location.search).get("lang");
  if (q === "en" || q === "pt") { store("l2-lang", q); return q; }
  const saved = store("l2-lang");
  if (saved === "en" || saved === "pt") return saved;
  return (navigator.language || "en").toLowerCase().startsWith("pt") ? "pt" : "en";
})();
const T = I18N[LANG];
function t(key, vars = {}) {
  return (T[key] ?? I18N.en[key] ?? key).replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");
}
const fmt = new Intl.NumberFormat(LANG === "pt" ? "pt-BR" : "en");
const num = (n) => (n === null || n === undefined ? "–" : fmt.format(n));
const when = (iso) => (iso ? iso.replace("T", " ").replace(/(:\d\d)?\+00:00$|Z$/, "$1").slice(0, 16) : "–");
const short = (sha) => (sha ? sha.slice(0, 12) + "…" : "–");

function applyLanguage() {
  document.documentElement.lang = LANG === "pt" ? "pt-BR" : "en";
  document.querySelectorAll("[data-i18n]").forEach((n) => { n.textContent = t(n.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((n) => { n.placeholder = t(n.dataset.i18nPlaceholder); });
  for (const lang of ["en", "pt"]) {
    const link = el(`lang-${lang}`);
    const u = new URL(location.href);
    u.searchParams.set("lang", lang);
    link.href = u.search;
    link.classList.toggle("current", lang === LANG);
  }
}

// --- page ------------------------------------------------------------------------------------
let PAGE = null;
const LISTS = {};          // rule id -> promise of data/rules/<id>.json

function tile(label, value, note, cls) {
  return h("div", { class: "tile" }, h("div", { class: "label" }, label),
    h("div", { class: "value" + (cls ? " status " + cls : "") }, value), h("div", { class: "note" }, note));
}

function renderTiles() {
  const s = PAGE.totals;
  const evaluated = PAGE.rules.filter((r) => r.status === "evaluated");
  const records = evaluated.reduce((a, r) => a + (r.total || 0), 0);
  const files = new Set();
  for (const r of evaluated) for (const d of r.datasets) files.add(d.label);
  el("tiles").replaceChildren(
    tile(t("t_rules"), `${num(s.evaluated)} / ${num(s.rules)}`,
      s.not_evaluated ? t("t_rules_note", { n: s.not_evaluated }) : t("t_rules_all"), s.not_evaluated ? "bad" : ""),
    tile(t("t_signals"), num(s.signals), t("t_signals_note", { n: evaluated.filter((r) => r.signals).length }),
      s.signals ? "warn" : ""),
    tile(t("t_sources"), `${num(s.sources_ok)} / ${num(s.sources)}`,
      s.sources_ok < s.sources ? t("t_sources_note", { n: s.sources - s.sources_ok }) : t("t_sources_all"),
      s.sources_ok < s.sources ? "bad" : "good"),
    tile(t("t_records"), num(records), t("t_records_note", { n: files.size })),
  );
}

// rule order: "custom" uses the ids saved by the visitor; new rules go to the end in file order
function orderedRules() {
  const mode = el("order").value;
  const rules = [...PAGE.rules];
  if (mode === "signals") rules.sort((a, b) => (b.signals ?? -1) - (a.signals ?? -1) || a.file.localeCompare(b.file));
  else if (mode === "title") rules.sort((a, b) => (a.title || a.id).localeCompare(b.title || b.id, LANG));
  else if (mode === "file") rules.sort((a, b) => a.file.localeCompare(b.file));
  else {
    const saved = store("l2-order") || [];
    const pos = (r) => { const i = saved.indexOf(r.id); return i < 0 ? saved.length : i; };
    rules.sort((a, b) => pos(a) - pos(b) || a.file.localeCompare(b.file));
  }
  const q = el("rule-search").value.trim().toLowerCase();
  return q ? rules.filter((r) => [r.id, r.title, r.text, r.file].join(" ").toLowerCase().includes(q)) : rules;
}

function move(id, delta) {
  const ids = orderedRules().map((r) => r.id);
  const all = (store("l2-order") || []).filter((x) => PAGE.rules.some((r) => r.id === x));
  for (const r of PAGE.rules) if (!all.includes(r.id)) all.push(r.id);
  // apply the move on the visible sequence, then rebuild the full saved order around it
  const i = ids.indexOf(id), j = i + delta;
  if (i < 0 || j < 0 || j >= ids.length) return;
  [ids[i], ids[j]] = [ids[j], ids[i]];
  const rest = all.filter((x) => !ids.includes(x));
  store("l2-order", [...ids, ...rest]);
  el("order").value = "custom";
  store("l2-sort", "custom");
  renderRules();
}

function outcomeLabel(o) { return t("out_" + o); }

function ruleHistory(rule) {
  const rows = PAGE.history.filter((run) => run.rules && run.rules[rule.id]).slice(-12).reverse();
  if (rows.length <= 1) return h("p", { class: "muted" }, t("hist_none"));
  return h("table", { class: "mini hist" },
    h("tr", {}, h("th", {}, t("h_run")), ...SIGNAL_OUTCOMES.map((o) => h("th", {}, outcomeLabel(o)))),
    rows.map((run) => {
      const r = run.rules[rule.id];
      return h("tr", {}, h("td", { class: "when" }, when(run.at)),
        r.status === "evaluated"
          ? SIGNAL_OUTCOMES.map((o) => h("td", {}, num(r.counts?.[o])))
          : h("td", { colspan: SIGNAL_OUTCOMES.length, class: "crit" }, t("not_evaluated")));
    }));
}

async function showList(rule, outcome, panel, button) {
  if (!panel.hidden && panel.dataset.outcome === outcome) {
    panel.hidden = true; button.textContent = t("see_list"); return;
  }
  panel.closest(".card").querySelectorAll(".outcome button").forEach((b) => { b.textContent = t("see_list"); });
  panel.hidden = false;
  panel.dataset.outcome = outcome;
  button.textContent = t("hide_list");
  panel.replaceChildren(h("p", { class: "muted" }, t("loading_list")));
  LISTS[rule.id] ??= fetch(`data/${rule.list}`, { cache: "no-cache" }).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
  let data;
  try { data = await LISTS[rule.id]; } catch (e) { delete LISTS[rule.id]; panel.replaceChildren(h("p", { class: "crit" }, t("list_error"))); return; }
  const byFile = data.records?.[outcome] || {};
  const sha = data.sources[rule.evaluated_source]?.sha256;
  const subset = { rule: data.rule, version: data.version, evaluated_at: data.evaluated_at, outcome,
    numbering: data.numbering, source_sha256: sha, records: byFile };
  const blob = URL.createObjectURL(new Blob([JSON.stringify(subset, null, 1)], { type: "application/json" }));
  const files = Object.entries(byFile).map(([file, nums]) => {
    const line = h("div", { class: "nums" }, nums.slice(0, LIST_PREVIEW).join(", ") + (nums.length > LIST_PREVIEW ? " …" : ""));
    const more = nums.length > LIST_PREVIEW
      ? h("button", { class: "showmore", type: "button", onclick: (ev) => { line.textContent = nums.join(", "); ev.target.remove(); } },
        t("show_all", { n: num(nums.length) }))
      : null;
    return [h("div", { class: "file" }, `${file} · ${num(nums.length)}`), line, more];
  });
  panel.replaceChildren(
    h("div", { class: "tools" },
      h("a", { href: blob, download: `${rule.id}.${outcome}.json` }, t("download")),
      h("a", { href: `data/${rule.list}`, target: "_blank", rel: "noopener" }, t("download_all"))),
    h("p", { class: "muted small" }, t("numbering", { sha: short(sha) })),
    files);
}

function card(rule, index, count) {
  const head = h("div", { class: "card-head" },
    h("div", {}, h("h3", {}, rule.title || rule.id), h("div", { class: "id" }, `${rule.file} · v${rule.version || "?"}`)),
    h("div", { class: "move" },
      h("button", { type: "button", title: t("up"), "aria-label": t("up"), disabled: index === 0, onclick: () => move(rule.id, -1) }, "↑"),
      h("button", { type: "button", title: t("down"), "aria-label": t("down"), disabled: index === count - 1, onclick: () => move(rule.id, 1) }, "↓")));
  const datasets = h("div", { class: "datasets-line" }, `${t("datasets")}: `, rule.datasets.map((d) => d.label).join("  ·  "));
  const panel = h("div", { class: "list-panel", hidden: true });
  let result;
  if (rule.status !== "evaluated") {
    result = h("div", { class: "result" }, h("span", { class: "status bad" }, t("not_evaluated")),
      h("span", { class: "muted small" }, `${t("reason")}: ${rule.reason || rule.reason_code}`));
  } else {
    const parts = SIGNAL_OUTCOMES.filter((o) => rule.counts[o] > 0).map((o) => {
      const b = h("button", { type: "button", onclick: () => showList(rule, o, panel, b) }, t("see_list"));
      return h("span", { class: "outcome", title: t("tip_" + o) }, h("strong", {}, num(rule.counts[o])), outcomeLabel(o), " [", b, "]");
    });
    result = h("div", { class: "result" },
      rule.signals
        ? h("span", { class: "big status warn" }, t("signals_at", { n: num(rule.signals), d: when(rule.evaluated_at) }))
        : h("span", { class: "big status good" }, t("no_signal", { d: when(rule.evaluated_at) })),
      h("span", { class: "muted small" }, t("of_records", { n: num(rule.total) })),
      h("div", { style: "flex-basis:100%;display:flex;flex-wrap:wrap;gap:6px 18px" }, parts));
  }
  const details = (key, body) => h("details", {}, h("summary", {}, t(key)), h("div", {}, body));
  return h("article", { class: "card", lang: rule.language || null },
    head,
    rule.text ? h("p", { style: "margin:4px 0" }, rule.text) : null,
    datasets,
    details("justification", h("p", {}, rule.justification || "–")),
    details("exceptions", rule.exceptions?.length ? h("ul", {}, rule.exceptions.map((e) => h("li", {}, e))) : h("p", {}, t("no_exceptions"))),
    rule.examples?.length ? details("examples", h("ul", {}, rule.examples.map((e) => h("li", {}, e.case, " → ", h("em", {}, e.expected))))) : null,
    details("history", ruleHistory(rule)),
    result, panel);
}

function renderRules() {
  const rules = orderedRules();
  const box = el("rules");
  box.replaceChildren();
  if (!el("group").checked) { rules.forEach((r, i) => box.append(card(r, i, rules.length))); return; }
  const folders = [...new Set(rules.map((r) => r.folder))].sort();
  for (const f of folders) {
    const inFolder = rules.filter((r) => r.folder === f);
    box.append(h("h3", { class: "group-h" }, f ? `rules/${f}/` : t("root_folder")));
    inFolder.forEach((r, i) => box.append(card(r, i, inFolder.length)));
  }
}

function renderSources() {
  el("sources").replaceChildren(
    h("tr", {}, ["s_resource", "s_status", "s_portal", "s_download", "s_modified", "s_sha", "s_used"].map((k) => h("th", {}, t(k)))),
    ...PAGE.sources.map((s) => {
      const ok = s.status === "ok";
      const portal = s.package_show?.http_status ? `HTTP ${s.package_show.http_status} · ${s.package_show.seconds} s` : (s.package_show?.error || "–");
      const dl = s.download?.bytes !== undefined ? `${(s.download.bytes / 1e6).toFixed(1)} MB · ${s.download.seconds} s` : (s.download?.error || "–");
      return h("tr", {},
        h("td", {}, h("a", { href: `${s.portal}/dataset/${s.dataset_name}`, target: "_blank", rel: "noopener" }, s.label)),
        h("td", {}, h("span", { class: "status " + (ok ? "good" : "bad") }, t("st_" + s.status)), ok ? null : h("div", { class: "muted small" }, s.reason)),
        h("td", { class: "when" }, portal), h("td", { class: "when" }, dl),
        h("td", { class: "when" }, when(s.resource?.metadata_modified || s.dataset?.metadata_modified)),
        h("td", {}, h("code", { title: s.download?.sha256 || "" }, short(s.download?.sha256))),
        h("td", {}, (s.used_by || []).join(", ")));
    }));
}

function renderHistory() {
  const ids = PAGE.rules.map((r) => r.id);
  const runs = [...PAGE.history].reverse();
  el("history").replaceChildren(
    h("tr", {}, h("th", {}, t("h_run")), h("th", {}, t("h_env")), h("th", { class: "num" }, t("h_sources")),
      ids.map((id) => h("th", { class: "num" }, `${id} (${t("h_signals")})`))),
    ...runs.map((run) => {
      const src = Object.values(run.sources || {});
      const okN = src.filter((s) => s === "ok").length;
      return h("tr", {}, h("td", { class: "when" }, when(run.at)),
        h("td", {}, run.environment === "local" ? t("env_local") : t("env_actions")),
        h("td", { class: "num" + (okN < src.length ? " crit" : "") }, `${okN}/${src.length}`),
        ids.map((id) => {
          const r = run.rules?.[id];
          if (!r) return h("td", { class: "num muted" }, "–");
          if (r.status !== "evaluated") return h("td", { class: "num crit" }, "✕");
          return h("td", { class: "num" }, num(SIGNAL_OUTCOMES.reduce((a, o) => a + (r.counts?.[o] || 0), 0)));
        }));
    }));
}

function renderProvenance() {
  const e = PAGE.engine || {};
  const kv = [["k_env", PAGE.environment === "local" ? t("env_local") : t("env_actions")],
    ["k_started", when(PAGE.started_at)], ["k_finished", when(PAGE.generated_at)],
    ["k_commit", e.commit ? e.commit.slice(0, 12) : "–"], ["k_dirty", e.uncommitted_changes ? t("yes") : t("no")],
    ["k_python", e.python], ["k_duckdb", e.duckdb]];
  el("engine").replaceChildren(...kv.flatMap(([k, v]) => [h("span", {}, t(k)), h("span", { class: "v" }, v ?? "–")]),
    ...(PAGE.run_url ? [h("span", {}, t("k_run")), h("a", { class: "v", href: PAGE.run_url, target: "_blank", rel: "noopener" }, PAGE.run_id)] : []));
  const rows = [
    ...(PAGE.rule_files || []).map((r) => [t("hx_rule"), `${r.file} (v${r.version})`, r.sha256]),
    ...PAGE.sources.map((s) => [t("hx_source"), s.label, s.download?.sha256]),
  ];
  el("hashes").replaceChildren(h("tr", {}, h("th", {}, t("hx_kind")), h("th", {}, t("hx_name")), h("th", {}, t("hx_sha"))),
    ...rows.map(([k, n, sha]) => h("tr", {}, h("td", {}, k), h("td", { style: "text-align:left;overflow-wrap:anywhere" }, n),
      h("td", { style: "text-align:left" }, h("code", { title: sha || "" }, short(sha))))));
}

function renderDatasets() {
  el("datasets").replaceChildren(
    h("tr", {}, ["d_dataset", "d_org", "d_license", "d_rules"].map((k) => h("th", {}, t(k)))),
    ...PAGE.sources.map((s) => h("tr", {},
      h("td", {}, h("a", { href: `${s.portal}/dataset/${s.dataset_name}`, target: "_blank", rel: "noopener" },
        s.dataset?.title || s.dataset_name), h("div", { class: "muted small" }, new URL(s.portal).hostname)),
      h("td", {}, s.dataset?.organization || "–"), h("td", {}, s.dataset?.license || "–"),
      h("td", {}, (s.used_by || []).join(", ")))));
}

async function main() {
  applyLanguage();
  el("title").textContent = t("title");
  try {
    const resp = await fetch("data/layer2.json", { cache: "no-cache" });
    if (!resp.ok) throw new Error(resp.status);
    PAGE = await resp.json();
  } catch (e) {
    el("subtitle").textContent = t("no_data");
    document.querySelectorAll("main > section:not(.tiles)").forEach((s) => { s.hidden = true; });
    return;
  }
  el("subtitle").textContent = t("subtitle", { at: when(PAGE.generated_at) + " UTC",
    env: PAGE.environment === "local" ? t("env_local") : t("env_actions") });
  el("order").value = store("l2-sort") || "custom";
  el("group").checked = !!store("l2-group");
  el("order").addEventListener("change", () => { store("l2-sort", el("order").value); renderRules(); });
  el("group").addEventListener("change", () => { store("l2-group", el("group").checked); renderRules(); });
  el("rule-search").addEventListener("input", renderRules);
  renderTiles(); renderRules(); renderSources(); renderHistory(); renderProvenance(); renderDatasets();
  el("footer").replaceChildren(t("footer"), " ",
    h("a", { href: "data/layer2.json" }, "layer2.json"), " · ", h("a", { href: "data/status.json" }, "status.json"));
}

main();
