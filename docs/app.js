// 5L-TEP Layer 2 dashboard. Reads data/layer2.json and, on demand, data/rules/<id>.json (both written
// by `python main.py run`). No library, no build step. Every text from the data is inserted as text,
// never as HTML. The visitor's order of the rule cards is kept in localStorage and changes nothing
// in the evaluation.

const I18N = {
  en: {
    back: "← Back to the repository", eyebrow: "5L-TEP · Layer 2 · Semantic Policies", loading: "Loading…",
    title: "Semantic policies over open data", run: "Run now ↗", rules_btn: "Rule files ↗", manifest_btn: "Manifest ↗", signals_btn: "Latest results (plain text) ↗",
    intro: "Each rule crosses data published on CKAN open data portals. Every week this repository downloads each resource once, records whether each portal answered and what it served, and counts, for every rule, the records that deserve a second look. A signal is something to review, never a verdict on the data; no value from the portals is published here, only counts and record numbers.",
    subtitle: "Last run {at} · {env}", env_actions: "GitHub Actions", env_local: "local test run: not a published result",
    no_data: "No run has been published yet.",
    t_rules: "Rules evaluated", t_rules_note: "{n} not evaluated in this run", t_rules_all: "all rules evaluated",
    t_signals: "Signals to review", t_signals_note: "in {n} of {t} rules; {z} without signals", t_signals_all: "in all {t} rules",
    t_rate: "L2 pass rate", t_rate_note: "((checks − signals) / checks) × 100", f_checks: "checks", f_signals: "signals", t_rate_none: "no check in scope",
    t_sources: "Sources available", t_sources_note: "{n} failed", t_sources_all: "every portal answered",
    t_checks: "Checks in scope", t_checks_note: "one per record and rule; {o} records out of scope",
    rules_h: "Rules", order: "Order", o_custom: "Custom", o_signals: "Most signals first", o_title: "Title",
    o_file: "Folder and file", group: "group by folder", search_rules: "Search rules",
    order_note: "Use ↑ ↓ to arrange the cards: the order becomes Custom, kept in this browser only; it changes nothing in the evaluation.",
    chart_records: "Chart and records", out_invalid_value: "unreadable value",
    tip_invalid_value: "A value is present but cannot be read as the declared date or number.",
    lic_note: "Data of the publishers above, under the licences shown (link to each licence). This page publishes only results derived from the data (counts, record numbers and charts); the data themselves are not redistributed.",
    ph_table_h: "Seconds per phase", sp_table_h: "Speed per run",
    up: "Move up", down: "Move down", root_folder: "(rules/)",
    datasets: "Datasets", justification: "Justification", exceptions: "Exceptions", examples: "Examples", history: "History",
    no_exceptions: "None recorded.", expected: "Expected",
    chart_btn: "▸ Chart", chart_hide: "▾ Chart", ch_time_h: "Over time", ch_order_h: "In the order of the records",
    ch_time_note: "Flagged records per year of {col}.",
    ch_member_note: "Flagged records per file of the resource (each file is a year or a part of the publication).",
    ch_no_time: "This rule has no date to chart over time (no timeline, and the resource is a single file).",
    ch_order_note: "Flagged records along the {n} records read, in file order (dashed lines: start of each file). Clusters show where in the publication the signals are.",
    ch_count: "number of flagged records", ch_share: "% of the records evaluated in each period", ch_mode: "Show",
    ch_mode_note: "Evaluated records are those the rule applies to (records out of its scope are not counted). The percentage makes years with few and many records comparable.",
    ch_unknown: "{n} record(s) without a readable date",
    signals_at: "{n} flagged on {d}", signals_one: "1 flagged on {d}", of_records: "of {n} records",
    not_evaluated: "✕ Not evaluated in this run", no_signal: "✓ None flagged on {d}",
    list_btn: "▸ Record list", list_hide: "▾ Record list", go_section: "Go to the section",
    list_note: "Record numbers per file (1 = first line after the header), valid for the bytes with SHA-256 {sha}. Published file: {file}.",
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
    speed_h: "Download speed", table_view: "Table view",
    speed_note: "Megabytes per second in each run: total bytes over total download time, for the resources of this instance's portal and, separately, of the other portals the rules cross. It follows how fast the portals deliver their files over time; a slow run delays results but changes nothing in them.",
    sp_primary: "{name} (this instance's portal)", sp_secondary: "other portals", sp_run: "Run (UTC)", sp_mbps: "MB/s",
    sp_resources: "resources", sp_bytes: "MB", sp_none: "No download speed recorded yet.",
    sp_processing: "processing (MB/s of the downloaded data)",
    phases_h: "Time of each phase", phases_note: "Seconds per run: download, processing (reading the declared columns and evaluating the rules), writing the outputs, and the publish job's check and copy.",
    ph_download: "download", ph_processing: "processing", ph_outputs: "writing the outputs", ph_publish: "publication", ph_s: "s",
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
    manifest_btn: "Manifesto ↗", signals_btn: "Resultados recentes (texto simples) ↗",
    intro: "Cada regra cruza dados publicados em portais de dados abertos CKAN. Toda semana este repositório baixa cada recurso uma vez, registra se cada portal respondeu e o que entregou, e conta, para cada regra, os registros que merecem um segundo olhar. Um sinal é algo a revisar, nunca um veredito sobre os dados; nenhum valor dos portais é publicado aqui, só contagens e números de registro.",
    subtitle: "Última rodada {at} · {env}", env_actions: "GitHub Actions", env_local: "ensaio local: não é resultado publicado",
    no_data: "Nenhuma rodada foi publicada ainda.",
    t_rules: "Regras avaliadas", t_rules_note: "{n} não avaliada(s) nesta rodada", t_rules_all: "todas as regras avaliadas",
    t_signals: "Sinais a revisar", t_signals_note: "em {n} de {t} regras; {z} sem sinal", t_signals_all: "em todas as {t} regras",
    t_rate: "Taxa de aprovação L2", t_rate_note: "((verificações − sinais) / verificações) × 100", f_checks: "verificações", f_signals: "sinais", t_rate_none: "nenhuma verificação no escopo",
    t_sources: "Fontes disponíveis", t_sources_note: "{n} com falha", t_sources_all: "todos os portais responderam",
    t_checks: "Verificações no escopo", t_checks_note: "uma por registro e regra; {o} registros fora do escopo",
    rules_h: "Regras", order: "Ordem", o_custom: "Personalizada", o_signals: "Mais sinais primeiro", o_title: "Título",
    o_file: "Pasta e arquivo", group: "agrupar por pasta", search_rules: "Buscar regras",
    order_note: "Use ↑ ↓ para arrumar os cartões: a ordem vira Personalizada e fica só neste navegador; não muda nada na avaliação.",
    chart_records: "Gráfico e registros", out_invalid_value: "valor ilegível",
    tip_invalid_value: "O valor está presente, mas não se lê como a data ou o número declarado.",
    lic_note: "Dados dos publicadores acima, sob as licenças indicadas (link para cada licença). Esta página publica só resultados derivados dos dados (contagens, números de registro e gráficos); os dados em si não são redistribuídos.",
    ph_table_h: "Segundos por etapa", sp_table_h: "Velocidade por rodada",
    up: "Subir", down: "Descer", root_folder: "(rules/)",
    datasets: "Datasets", justification: "Justificativa", exceptions: "Exceções", examples: "Exemplos", history: "Histórico",
    no_exceptions: "Nenhuma registrada.", expected: "Esperado",
    chart_btn: "▸ Gráfico", chart_hide: "▾ Gráfico", ch_time_h: "Ao longo do tempo", ch_order_h: "Na ordem dos registros",
    ch_time_note: "Registros sinalizados por ano de {col}.",
    ch_member_note: "Registros sinalizados por arquivo do recurso (cada arquivo é um ano ou uma parte da publicação).",
    ch_no_time: "Esta regra não tem data para o gráfico no tempo (sem timeline, e o recurso é um arquivo só).",
    ch_order_note: "Registros sinalizados ao longo dos {n} registros lidos, na ordem dos arquivos (tracejado: início de cada arquivo). Agrupamentos mostram onde, na publicação, estão os sinais.",
    ch_count: "número de registros sinalizados", ch_share: "% dos registros avaliados em cada período", ch_mode: "Mostrar",
    ch_mode_note: "Registros avaliados são aqueles a que a regra se aplica (os fora do escopo não entram na conta). O percentual permite comparar anos com poucos e com muitos registros.",
    ch_unknown: "{n} registro(s) sem data legível",
    signals_at: "{n} sinalizados em {d}", signals_one: "1 sinalizado em {d}", of_records: "de {n} registros",
    not_evaluated: "✕ Não avaliada nesta rodada", no_signal: "✓ Nenhum sinalizado em {d}",
    list_btn: "▸ Lista de registros", list_hide: "▾ Lista de registros", go_section: "Ir para a seção",
    list_note: "Números de registro por arquivo (1 = primeira linha após o cabeçalho), válidos para os bytes com SHA-256 {sha}. Arquivo publicado: {file}.",
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
    speed_h: "Velocidade de download", table_view: "Ver como tabela",
    speed_note: "Megabytes por segundo em cada rodada: total de bytes dividido pelo tempo total de download, para os recursos do portal desta instância e, separadamente, dos demais portais que as regras cruzam. Mostra a velocidade com que os portais entregam os arquivos ao longo do tempo; uma rodada lenta atrasa os resultados, mas não muda nada neles.",
    sp_primary: "{name} (portal desta instância)", sp_secondary: "demais portais", sp_run: "Rodada (UTC)", sp_mbps: "MB/s",
    sp_resources: "recursos", sp_bytes: "MB", sp_none: "Nenhuma velocidade de download registrada ainda.",
    sp_processing: "processamento (MB/s dos dados baixados)",
    phases_h: "Tempo de cada etapa", phases_note: "Segundos por rodada: download, processamento (leitura das colunas declaradas e avaliação das regras), gravação das saídas, e a conferência e cópia feitas pelo job de publicação.",
    ph_download: "download", ph_processing: "processamento", ph_outputs: "gravação das saídas", ph_publish: "publicação", ph_s: "s",
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

const SIGNAL_OUTCOMES = ["mismatch", "key_not_found", "missing_value", "invalid_value", "ambiguous_key"];
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
// a number with up to `digits` decimals, in the page's language (0,58 in Portuguese, 0.58 in English)
const dec = (n, digits = 1) => (n === null || n === undefined || Number.isNaN(Number(n)) ? "–"
  : Number(n).toLocaleString(LANG === "pt" ? "pt-BR" : "en", { maximumFractionDigits: digits }));
// a percentage with two decimals, rounded down: 99,998% shows 99,99%, so only a rate without signals reads 100,00%
const pct = (rate) => (Math.floor(rate * 10000 + 1e-9) / 100).toLocaleString(LANG === "pt" ? "pt-BR" : "en",
  { minimumFractionDigits: 2, maximumFractionDigits: 2 });
// Dates in the format of the page's language, always in UTC: 09/10/2026 00:17 (pt), 9 Oct 2026, 00:17 (en).
// English uses the month's name, so that day and month are never confused.
const LOCALE = LANG === "pt" ? "pt-BR" : "en-GB";
const DATE_TIME = new Intl.DateTimeFormat(LOCALE, LANG === "pt"
  ? { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "UTC" }
  : { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "UTC" });
const DATE_ONLY = new Intl.DateTimeFormat(LOCALE, LANG === "pt"
  ? { day: "2-digit", month: "2-digit", year: "numeric", timeZone: "UTC" }
  : { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
const parseIso = (iso) => { const d = iso ? new Date(/[Zz]|[+-]\d\d:\d\d$/.test(iso) ? iso : iso + "Z") : null; return d && !isNaN(d) ? d : null; };
const when = (iso) => { const d = parseIso(iso); return d ? DATE_TIME.format(d) : "–"; };
const day = (iso) => { const d = parseIso(iso); return d ? DATE_ONLY.format(d) : "–"; };
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

// the L2 pass rate as a fraction with a horizontal bar (MathML, drawn by the browser; t_rate_note is the text form)
function rateFormula() {
  const m = (tag, ...kids) => {
    const node = document.createElementNS("http://www.w3.org/1998/Math/MathML", tag);
    for (const k of kids) node.append(typeof k === "string" ? document.createTextNode(k) : k);
    return node;
  };
  const word = (s) => m("mtext", s);
  const math = m("math", m("mrow",
    m("mfrac", m("mrow", word(t("f_checks")), m("mo", "−"), word(t("f_signals"))), word(t("f_checks"))),
    m("mo", "×"), m("mn", "100")));
  math.setAttribute("displaystyle", "true");  // numerator and denominator at full size
  math.setAttribute("aria-label", t("t_rate_note"));
  return math;
}

function tile(label, value, note, cls, target) {
  const go = () => el(target)?.scrollIntoView({ behavior: "smooth", block: "start" });
  return h("div", { class: "tile" + (target ? " go" : ""), role: target ? "link" : null, tabindex: target ? "0" : null,
    title: target ? t("go_section") : null, onclick: target ? go : null,
    onkeydown: target ? (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); go(); } } : null },
    h("div", { class: "label" }, label),
    h("div", { class: "value" + (cls ? " status " + cls : "") }, value), h("div", { class: "note" }, note));
}

function renderTiles() {
  const s = PAGE.totals;
  const evaluated = PAGE.rules.filter((r) => r.status === "evaluated");
  const flagged = evaluated.filter((r) => r.signals).length;
  const outOfScope = evaluated.reduce((a, r) => a + ((r.counts || {}).out_of_scope || 0), 0);
  // L2 pass rate (layer2.json since 09/10/2026; computed from the rules for data published before that)
  const checks = s.checks ?? evaluated.reduce((a, r) => a + (r.total || 0) - ((r.counts || {}).out_of_scope || 0), 0);
  const rate = s.l2_rate !== undefined ? s.l2_rate : (checks ? 1 - s.signals / checks : null);
  el("tiles").replaceChildren(
    tile(t("t_rules"), `${num(s.evaluated)} / ${num(s.rules)}`,
      s.not_evaluated ? t("t_rules_note", { n: s.not_evaluated }) : t("t_rules_all"), s.not_evaluated ? "bad" : "", "rules-section"),
    tile(t("t_sources"), `${num(s.sources_ok)} / ${num(s.sources)}`,
      s.sources_ok < s.sources ? t("t_sources_note", { n: s.sources - s.sources_ok }) : t("t_sources_all"),
      s.sources_ok < s.sources ? "bad" : "good", "sources-section"),
    tile(t("t_signals"), num(s.signals), flagged === evaluated.length ? t("t_signals_all", { t: num(evaluated.length) })
      : t("t_signals_note", { n: num(flagged), t: num(evaluated.length), z: num(evaluated.length - flagged) }),
      s.signals ? "warn" : "", "rules-section"),
    tile(t("t_checks"), num(checks), t("t_checks_note", { o: num(outOfScope) }), "", "rules-section"),
    tile(t("t_rate"), rate === null ? "–" : `${pct(rate)}%`,
      rate === null ? t("t_rate_none") : rateFormula(), "", "rules-section"),
  );
}

// rule order: "signals" by default; "custom" uses the ids saved by the visitor (a move under any other
// order starts the custom order from the order on screen); new rules go to the end in file order
function orderedRules() {
  const mode = el("order").value;
  const rules = [...PAGE.rules];
  if (mode === "signals") rules.sort((a, b) => (b.signals ?? -1) - (a.signals ?? -1) || a.file.localeCompare(b.file));
  else if (mode === "title") rules.sort((a, b) => ruleTitle(a).text.localeCompare(ruleTitle(b).text, LANG));
  else if (mode === "file") rules.sort((a, b) => a.file.localeCompare(b.file));
  else {
    const saved = store("l2-order") || [];
    const pos = (r) => { const i = saved.indexOf(r.id); return i < 0 ? saved.length : i; };
    rules.sort((a, b) => pos(a) - pos(b) || a.file.localeCompare(b.file));
  }
  const q = el("rule-search").value.trim().toLowerCase();
  return q ? rules.filter((r) => [r.id, r.title, ...Object.values(r.title_translations || {}), r.text, r.file]
    .join(" ").toLowerCase().includes(q)) : rules;
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

// The rule's title in the dashboard's language when the rule has one (description.language or
// title_translations, matched by primary language subtag), else the title it has.
function ruleTitle(rule) {
  const primary = (tag) => (tag || "").toLowerCase().split("-")[0];
  if (primary(rule.language) === LANG) return { text: rule.title || rule.id, lang: rule.language };
  const match = Object.entries(rule.title_translations || {}).find(([tag]) => primary(tag) === LANG);
  return match ? { text: match[1], lang: match[0] } : { text: rule.title || rule.id, lang: rule.language };
}

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

async function showList(rule, panel) {
  panel.replaceChildren(h("p", { class: "muted" }, t("loading_list")));
  let data;
  try { data = await loadList(rule); } catch (e) { panel.replaceChildren(h("p", { class: "crit" }, t("list_error"))); return; }
  const src = data.sources?.[rule.evaluated_source] || {};
  const file = src.file ? (src.archive_members ? `${src.file} (${src.archive_members})` : src.file) : "–";
  const sections = SIGNAL_OUTCOMES.filter((o) => Object.keys(data.records?.[o] || {}).length).map((o) => {
    const byFile = data.records[o];
    const subset = { rule: data.rule, rule_version: data.rule_version, evaluated_at: data.evaluated_at, outcome: o,
      numbering: data.numbering, source_file: src.file, source_url: src.url, archive_members: src.archive_members,
      source_sha256: src.sha256, records: byFile };
    const blob = URL.createObjectURL(new Blob([JSON.stringify(subset, null, 1)], { type: "application/json" }));
    const files = Object.entries(byFile).map(([f, nums]) => {
      const line = h("div", { class: "nums" }, nums.slice(0, LIST_PREVIEW).join(", ") + (nums.length > LIST_PREVIEW ? " …" : ""));
      const more = nums.length > LIST_PREVIEW
        ? h("button", { class: "showmore", type: "button", onclick: (ev) => { line.textContent = nums.join(", "); ev.target.remove(); } },
          t("show_all", { n: num(nums.length) }))
        : null;
      return [h("div", { class: "file" }, `${f} · ${num(nums.length)}`), line, more];
    });
    return [h("h4", {}, `${outcomeLabel(o)} · ${num(rule.counts[o])} `,
      h("a", { href: blob, download: `${rule.id}.${o}.json`, class: "small" }, t("download"))), files];
  });
  panel.replaceChildren(
    h("p", { class: "muted small" }, t("list_note", { sha: short(src.sha256), file }), " ",
      h("a", { href: `data/rules/${encodeURIComponent(rule.id)}.json`, target: "_blank", rel: "noopener" }, t("download_all"))),
    ...sections.flat(Infinity).filter(Boolean));
}

function loadList(rule) {
  LISTS[rule.id] ??= fetch(`data/rules/${encodeURIComponent(rule.id)}.json`, { cache: "no-cache" })
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
  return LISTS[rule.id].catch((e) => { delete LISTS[rule.id]; throw e; });
}

// Grid values for an axis from 0 to max: whole numbers when the counts are small.
function ticks(max, whole) {
  if (whole && max <= 8) return Array.from({ length: Math.max(1, Math.ceil(max)) + 1 }, (_, i) => i);
  return [0, 1, 2, 3, 4].map((i) => (max * i) / 4);
}

// Stacked bars of signal outcomes per category (year or file); mode "count" or "share".
function stackedBars(categories, mode, label) {
  const W = 860, H = 220, L = 52, B = 40, T = 22;
  const value = (c, o) => (mode === "share" ? (c.inScope ? (100 * (c.counts[o] || 0)) / c.inScope : 0) : c.counts[o] || 0);
  let max = Math.max(1, ...categories.map((c) => SIGNAL_OUTCOMES.reduce((a, o) => a + value(c, o), 0)));
  if (mode !== "share" && max <= 8) max = Math.ceil(max);
  const step = (W - L - 10) / Math.max(1, categories.length), bw = Math.max(2, Math.min(26, step * 0.7));
  const y = (v) => T + (H - T - B) * (1 - v / max);
  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": label });
  for (const v of ticks(max, mode !== "share")) {
    svg.append(s("line", { class: "grid", x1: L, x2: W - 10, y1: y(v), y2: y(v) }),
      s("text", { class: "axis-label", x: L - 6, y: y(v) + 4, "text-anchor": "end" },
        mode === "share" ? `${dec(v, v < 10 ? 1 : 0)}%` : num(Math.round(v))));
  }
  const every = Math.ceil(categories.length / 12);
  categories.forEach((c, i) => {
    let base = 0;
    const x = L + i * step + (step - bw) / 2;
    const signals = SIGNAL_OUTCOMES.reduce((a, o) => a + (c.counts[o] || 0), 0);
    SIGNAL_OUTCOMES.forEach((o) => {
      const v = value(c, o);
      if (!v) return;
      const rect = s("rect", { x, y: y(base + v), width: bw, height: Math.max(1, y(base) - y(base + v)),
        style: `fill:var(--out-${o})` });
      rect.append(s("title", {}, `${c.label} · ${outcomeLabel(o)}: ${num(c.counts[o] || 0)}` +
        (c.inScope ? ` (${dec((100 * (c.counts[o] || 0)) / c.inScope, 2)}%)` : "") +
        ` · ${num(signals)} / ${num(c.inScope)} ${LANG === "pt" ? "avaliados" : "evaluated"}`));
      svg.append(rect);
      base += v;
    });
    if (i % every === 0) svg.append(s("text", { class: "axis-label", x: x + bw / 2, y: H - 22, "text-anchor": "middle" }, c.label));
  });
  return svg;
}

// Histogram of signal positions along the records read (files concatenated in order).
function orderHistogram(data, label) {
  const members = data.members || [];
  const total = members.reduce((a, m) => a + m.records, 0);
  const offset = {};
  members.reduce((a, m) => { offset[m.name] = a; return a + m.records; }, 0);
  const BINS = 60, size = Math.max(1, Math.ceil(total / BINS));
  const bins = Array.from({ length: BINS }, () => ({}));
  for (const o of SIGNAL_OUTCOMES) {
    for (const [file, nums] of Object.entries(data.records?.[o] || {})) {
      for (const n of nums) {
        const b = Math.min(BINS - 1, Math.floor((offset[file] + n - 1) / size));
        bins[b][o] = (bins[b][o] || 0) + 1;
      }
    }
  }
  const W = 860, H = 200, L = 52, B = 30, T = 18;
  let max = Math.max(1, ...bins.map((b) => SIGNAL_OUTCOMES.reduce((a, o) => a + (b[o] || 0), 0)));
  if (max <= 8) max = Math.ceil(max);
  const step = (W - L - 10) / BINS;
  const y = (v) => T + (H - T - B) * (1 - v / max);
  const x = (pos) => L + ((W - L - 10) * pos) / Math.max(1, total);
  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": label });
  for (const v of ticks(max, true)) {
    svg.append(s("line", { class: "grid", x1: L, x2: W - 10, y1: y(v), y2: y(v) }),
      s("text", { class: "axis-label", x: L - 6, y: y(v) + 4, "text-anchor": "end" }, num(Math.round(v))));
  }
  if (members.length > 1) {
    // a line where each file starts, and its label, only where there is room (old files can be tiny)
    let lastLine = -Infinity, lastLabel = -Infinity;
    members.forEach((m) => {
      const px = x(offset[m.name]);
      if (px - lastLine >= 4) {
        svg.append(s("line", { class: "boundary", x1: px, x2: px, y1: T, y2: H - B }));
        lastLine = px;
      }
      if (px - lastLabel >= 44 && px <= W - 40) {
        svg.append(s("text", { class: "axis-label", x: px + 2, y: H - 12 }, (m.name.match(/\d{4}/g) || [m.name]).pop()));
        lastLabel = px;
      }
    });
  }
  bins.forEach((b, i) => {
    let base = 0;
    SIGNAL_OUTCOMES.forEach((o) => {
      const v = b[o] || 0;
      if (!v) return;
      const rect = s("rect", { x: L + i * step + 0.5, y: y(base + v), width: Math.max(1, step - 1),
        height: Math.max(1, y(base) - y(base + v)), style: `fill:var(--out-${o})` });
      rect.append(s("title", {}, `${num(i * size + 1)}–${num(Math.min(total, (i + 1) * size))} · ${outcomeLabel(o)}: ${num(v)}`));
      svg.append(rect);
      base += v;
    });
  });
  return svg;
}

async function showChart(rule, panel) {
  panel.replaceChildren(h("p", { class: "muted" }, t("loading_list")));
  let data;
  try { data = await loadList(rule); } catch (e) { panel.replaceChildren(h("p", { class: "crit" }, t("list_error"))); return; }
  const legend = h("ul", { class: "legend" }, SIGNAL_OUTCOMES.filter((o) => rule.counts[o] > 0).map((o) =>
    h("li", {}, h("span", { class: "swatch", style: `background:var(--out-${o})` }), outcomeLabel(o))));
  // over time: per year of the timeline column, else per file of the resource
  let cats = [], note = "", unknown = 0;
  if (Object.keys(data.by_period || {}).length) {
    unknown = Object.values(data.by_period.unknown || {}).reduce((a, n) => a + n, 0);
    cats = Object.entries(data.by_period).filter(([k]) => k !== "unknown").sort(([a], [b]) => a.localeCompare(b));
    note = t("ch_time_note", { col: (data.timeline || "").split(".").slice(1).join(".") });
  } else if (Object.keys(data.by_member || {}).length > 1) {
    cats = Object.entries(data.by_member).sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }));
    cats = cats.map(([k, v]) => [(k.match(/\d{4}/g) || [k]).pop(), v]);
    note = t("ch_member_note");
  }
  const categories = cats.map(([label, counts]) => ({ label, counts,
    inScope: Object.entries(counts).reduce((a, [o, n]) => a + (o === "out_of_scope" ? 0 : n), 0) }));
  const timeBox = h("div", { class: "chart" });
  const mode = h("select", { "aria-label": t("ch_mode") }, h("option", { value: "count" }, t("ch_count")), h("option", { value: "share" }, t("ch_share")));
  const drawTime = () => timeBox.replaceChildren(stackedBars(categories, mode.value, t("ch_time_h")));
  mode.addEventListener("change", drawTime);
  const total = (data.members || []).reduce((a, m) => a + m.records, 0);
  panel.replaceChildren(legend,
    h("h4", {}, t("ch_time_h")),
    ...(categories.length
      ? [h("p", { class: "note" }, note, unknown ? ` ${t("ch_unknown", { n: num(unknown) })}.` : ""),
         h("p", { class: "note" }, h("label", {}, `${t("ch_mode")}: `, mode)), h("p", { class: "note" }, t("ch_mode_note")), timeBox]
      : [h("p", { class: "note" }, t("ch_no_time"))]),
    h("h4", {}, t("ch_order_h")),
    h("p", { class: "note" }, t("ch_order_note", { n: num(total) })),
    h("div", { class: "chart" }, orderHistogram(data, t("ch_order_h"))));
  if (categories.length) drawTime();
}

function card(rule, index, count) {
  const head = h("div", { class: "card-head" },
    h("div", {}, h("h3", { lang: ruleTitle(rule).lang || null }, ruleTitle(rule).text),
      h("div", { class: "id" }, `${rule.file} · v${rule.rule_version || "?"}`)),
    h("div", { class: "move" },
      h("button", { type: "button", title: t("up"), "aria-label": t("up"), disabled: index === 0, onclick: () => move(rule.id, -1) }, "↑"),
      h("button", { type: "button", title: t("down"), "aria-label": t("down"), disabled: index === count - 1, onclick: () => move(rule.id, 1) }, "↓")));
  const datasets = h("div", { class: "datasets-line" }, `${t("datasets")}: `, rule.datasets.map((d) => d.label).join("  ·  "));
  let result;
  if (rule.status !== "evaluated") {
    result = h("div", { class: "result" }, h("span", { class: "status bad" }, t("not_evaluated")),
      h("span", { class: "muted small" }, `${t("reason")}: ${rule.reason || rule.reason_code}`));
  } else {
    const d = when(rule.evaluated_at);
    const headline = rule.signals === 0 ? t("no_signal", { d }) : rule.signals === 1 ? t("signals_one", { d })
      : t("signals_at", { n: num(rule.signals), d });
    const parts = SIGNAL_OUTCOMES.filter((o) => rule.counts[o] > 0).map((o) =>
      h("span", { class: "outcome", title: t("tip_" + o) }, h("strong", {}, num(rule.counts[o])), " ", outcomeLabel(o)));
    result = h("div", { class: "result" },
      h("span", { class: "big status " + (rule.signals ? "warn" : "good") }, headline),
      h("span", { class: "muted small" }, t("of_records", { n: num(rule.total) })),
      parts.length ? h("div", { class: "breakdown" }, parts) : null);
  }
  const details = (key, body) => h("details", {}, h("summary", {}, t(key)), h("div", {}, body));
  // chart and record list in one accordion, filled the first time it opens (the list only when exposure allows)
  let chartRecords = null;
  if (rule.status === "evaluated" && rule.signals) {
    const chartPanel = h("div", { class: "chart-panel" });
    const listPanel = rule.exposure !== "counts" ? h("div", { class: "list-panel" }) : null;
    chartRecords = h("details", { class: "chart-records", "data-chart": rule.id },
      h("summary", {}, t("chart_records")), h("div", {}, chartPanel, listPanel));
    let filled = false;
    chartRecords.addEventListener("toggle", () => {
      if (!chartRecords.open || filled) return;
      filled = true;
      showChart(rule, chartPanel);
      if (listPanel) showList(rule, listPanel);
    });
  }
  return h("article", { class: "card", lang: rule.language || null },
    head,
    rule.text ? h("p", { style: "margin:4px 0" }, rule.text) : null,
    datasets,
    result,
    h("div", { class: "toggles" },
      details("justification", h("p", {}, rule.justification || "–")),
      details("exceptions", rule.exceptions?.length ? h("ul", {}, rule.exceptions.map((e) => h("li", {}, e))) : h("p", {}, t("no_exceptions"))),
      rule.examples?.length ? details("examples", h("ul", {}, rule.examples.map((e) => h("li", {}, e.case, " → ", h("em", {}, e.expected))))) : null,
      details("history", ruleHistory(rule)), chartRecords));
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
      const portal = s.package_show?.http_status ? `HTTP ${s.package_show.http_status} · ${dec(s.package_show.seconds, 2)} s` : (s.package_show?.error || "–");
      const dl = s.download?.bytes !== undefined ? `${dec(s.download.bytes / 1e6, 1)} MB · ${dec(s.download.seconds, 1)} s` : (s.download?.error || "–");
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

const SVG = "http://www.w3.org/2000/svg";
function s(tag, attrs = {}, text) {
  const n = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text !== undefined) n.textContent = text;
  return n;
}

// Grouped bars: one pair (primary, secondary) per run, last 26 runs.
function renderSpeed() {
  const runs = PAGE.history.filter((r) => r.download_speed).slice(-26);
  const name = (() => { try { return new URL(PAGE.primary_portal).hostname; } catch (e) { return "portal"; } })();
  el("speed-legend").replaceChildren(
    h("li", {}, h("span", { class: "swatch", style: "background:var(--series-1)" }), t("sp_primary", { name })),
    h("li", {}, h("span", { class: "swatch", style: "background:var(--series-2)" }), t("sp_secondary")),
    h("li", {}, h("span", { class: "swatch", style: "background:var(--series-3)" }), t("sp_processing")));
  if (!runs.length) { el("speed-chart").replaceChildren(h("p", { class: "muted" }, t("sp_none"))); return; }
  const W = 860, H = 230, L = 44, B = 34, T = 26;
  const SERIES = ["primary", "secondary", "processing"];
  const max = Math.max(1, ...runs.flatMap((r) => SERIES.map((k) => r.download_speed[k]?.mb_per_s || 0)));
  const step = (W - L - 10) / runs.length, bw = Math.max(3, Math.min(18, step / 3.6));
  const y = (v) => T + (H - T - B) * (1 - v / max);
  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": t("speed_h") });
  for (let i = 0; i <= 4; i++) {
    const v = (max * i) / 4;
    svg.append(s("line", { class: "grid", x1: L, x2: W - 10, y1: y(v), y2: y(v) }),
      s("text", { class: "axis-label", x: L - 6, y: y(v) + 4, "text-anchor": "end" }, dec(v, v < 10 ? 1 : 0)));
  }
  runs.forEach((r, i) => {
    const x0 = L + i * step + step / 2 - 1.5 * bw;
    SERIES.forEach((k, j) => {
      const v = r.download_speed[k]?.mb_per_s;
      if (v === null || v === undefined) return;
      const rect = s("rect", { class: `bar-${k}`, x: x0 + j * bw, y: y(v), width: bw - 1, height: Math.max(1, y(0) - y(v)), rx: 2 });
      const label = k === "primary" ? t("sp_primary", { name }) : k === "secondary" ? t("sp_secondary") : t("sp_processing");
      rect.append(s("title", {}, `${when(r.at)} · ${label}: ${dec(v, 2)} MB/s`));
      svg.append(rect);
    });
    if (runs.length <= 8 || i % Math.ceil(runs.length / 8) === 0) {
      svg.append(s("text", { class: "axis-label", x: L + i * step + step / 2, y: H - 12, "text-anchor": "middle" }, day(r.at)));
    }
  });
  svg.append(s("text", { class: "axis-label", x: L - 6, y: 11, "text-anchor": "end" }, t("sp_mbps")));
  el("speed-chart").replaceChildren(svg);
  el("speed-table").replaceChildren(
    h("tr", {}, h("th", {}, t("sp_run")), h("th", {}, `${name} ${t("sp_mbps")}`), h("th", {}, t("sp_resources")), h("th", {}, t("sp_bytes")),
      h("th", {}, `${t("sp_secondary")} ${t("sp_mbps")}`), h("th", {}, t("sp_resources")), h("th", {}, t("sp_bytes")),
      h("th", {}, `${t("ph_processing")} ${t("sp_mbps")}`)),
    ...[...runs].reverse().map((r) => h("tr", {}, h("td", {}, when(r.at)),
      ...["primary", "secondary"].flatMap((k) => {
        const d = r.download_speed[k] || {};
        return [h("td", {}, dec(d.mb_per_s, 2)), h("td", {}, num(d.resources)), h("td", {}, d.bytes ? dec(d.bytes / 1e6, 1) : "–")];
      }), h("td", {}, dec(r.download_speed.processing?.mb_per_s, 2)))));
}

// Stacked bars: seconds of download, processing, outputs and publication per run (last 26 runs).
function renderPhases(publish) {
  const byRun = Object.fromEntries((publish || []).map((p) => [p.run_id, p.accept_s]));
  const runs = PAGE.history.filter((r) => r.timings).slice(-26);
  const PH = [["download", (r) => r.timings.download_s], ["processing", (r) => r.timings.processing_s],
    ["outputs", (r) => r.timings.outputs_s], ["publish", (r) => (r.run_id ? byRun[r.run_id] : undefined)]];
  el("phases-legend").replaceChildren(...PH.map(([k], i) => h("li", {},
    h("span", { class: "swatch", style: `background:var(--series-${[1, 3, 4, 5][i]})` }), t("ph_" + k))));
  if (!runs.length) { el("phases-chart").replaceChildren(h("p", { class: "muted" }, t("sp_none"))); return; }
  const W = 860, H = 230, L = 44, B = 34, T = 26;
  const total = (r) => PH.reduce((a, [, f]) => a + (f(r) || 0), 0);
  const max = Math.max(1, ...runs.map(total));
  const step = (W - L - 10) / runs.length, bw = Math.max(4, Math.min(28, step * 0.6));
  const y = (v) => T + (H - T - B) * (1 - v / max);
  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": t("phases_h") });
  for (let i = 0; i <= 4; i++) {
    const v = (max * i) / 4;
    svg.append(s("line", { class: "grid", x1: L, x2: W - 10, y1: y(v), y2: y(v) }),
      s("text", { class: "axis-label", x: L - 6, y: y(v) + 4, "text-anchor": "end" }, dec(v, 0)));
  }
  runs.forEach((r, i) => {
    let base = 0;
    const x = L + i * step + (step - bw) / 2;
    PH.forEach(([k, f]) => {
      const v = f(r);
      if (!v) return;
      const rect = s("rect", { class: `bar-${k}`, x, y: y(base + v), width: bw, height: Math.max(1, y(base) - y(base + v)) });
      rect.append(s("title", {}, `${when(r.at)} · ${t("ph_" + k)}: ${dec(v, 1)} ${t("ph_s")}`));
      svg.append(rect);
      base += v;
    });
    if (runs.length <= 8 || i % Math.ceil(runs.length / 8) === 0) {
      svg.append(s("text", { class: "axis-label", x: x + bw / 2, y: H - 12, "text-anchor": "middle" }, day(r.at)));
    }
  });
  svg.append(s("text", { class: "axis-label", x: L - 6, y: 11, "text-anchor": "end" }, t("ph_s")));
  el("phases-chart").replaceChildren(svg);
  el("phases-table").replaceChildren(
    h("tr", {}, h("th", {}, t("sp_run")), ...PH.map(([k]) => h("th", {}, `${t("ph_" + k)} (${t("ph_s")})`)), h("th", {}, "total")),
    ...[...runs].reverse().map((r) => h("tr", {}, h("td", {}, when(r.at)),
      ...PH.map(([, f]) => h("td", {}, dec(f(r), 1))), h("td", {}, dec(total(r), 1)))));
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
    ...(PAGE.rule_files || []).map((r) => [t("hx_rule"), `${r.file} (v${r.rule_version})`, r.sha256]),
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
      h("td", {}, s.dataset?.organization || "–"),
      h("td", {}, (() => {
        const name = s.dataset?.license, id = s.dataset?.license_id;
        const text = id && name && id !== name ? `${id} (${name})` : (name || id || "–");
        return s.dataset?.license_url ? h("a", { href: s.dataset.license_url, target: "_blank", rel: "noopener" }, text) : text;
      })()),
      h("td", {}, (s.used_by || []).join(", ")))));
}

// accordions: opening one in a card closes the ones open in the other cards
document.addEventListener("toggle", (ev) => {
  const opened = ev.target;
  if (!(opened instanceof HTMLDetailsElement) || !opened.open) return;
  const card = opened.closest(".card");
  if (!card) return;
  document.querySelectorAll(".card details[open]").forEach((d) => { if (d.closest(".card") !== card) d.open = false; });
}, true);

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
  // this instance's repository (portal.json) in every link to the default repository, and its portal's name
  const repo = PAGE.portal?.repository;
  if (repo && repo !== "lsp3cesarschool/5ltep-layer2") {
    document.querySelectorAll('a[href*="lsp3cesarschool/5ltep-layer2"]').forEach((a) => {
      a.href = a.href.replace("lsp3cesarschool/5ltep-layer2", repo);
    });
  }
  if (PAGE.portal?.name) {
    document.querySelector(".eyebrow").textContent = `${t("eyebrow")} · ${PAGE.portal.name}`;
    document.title = `5L-TEP L2 · ${PAGE.portal.name}`;
  }
  el("subtitle").textContent = t("subtitle", { at: when(PAGE.generated_at) + " UTC",
    env: PAGE.environment === "local" ? t("env_local") : t("env_actions") });
  el("order").value = store("l2-sort") || "signals";
  el("group").checked = !!store("l2-group");
  el("order").addEventListener("change", () => { store("l2-sort", el("order").value); renderRules(); });
  el("group").addEventListener("change", () => { store("l2-group", el("group").checked); renderRules(); });
  el("rule-search").addEventListener("input", renderRules);
  renderTiles(); renderRules(); renderSources(); renderSpeed(); renderHistory(); renderProvenance(); renderDatasets();
  // a link to a chart: #grafico=<rule id> (or #chart=<rule id>) opens it and scrolls to its card
  const wanted = decodeURIComponent((location.hash.match(/^#(?:grafico|chart)=(.+)$/) || [])[1] || "");
  if (wanted) {
    const acc = document.querySelector(`details[data-chart="${CSS.escape(wanted)}"]`);
    if (acc) { acc.open = true; acc.closest(".card").scrollIntoView(); }
  }
  fetch("data/publish.json", { cache: "no-cache" }).then((r) => (r.ok ? r.json() : [])).catch(() => []).then(renderPhases);
  el("footer").replaceChildren(t("footer"), " ",
    h("a", { href: "data/layer2.json" }, "layer2.json"), " · ", h("a", { href: "data/status.json" }, "status.json"));
}

main();
