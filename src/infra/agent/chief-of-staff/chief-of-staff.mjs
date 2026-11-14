// chief-of-staff.mjs — Chief of Staff Local (plano padrão, Fase 4).
//
// Agente mínimo (adaptador `process` do Paperclip) com DOIS modos:
//  - TRIAGEM (default): lê a tarefa, consulta o auxiliar e registra a sugestão
//    JSON na issue, com handoff in_review ao responsável.
//  - PLANEJAMENTO (quando a descrição contém "MODO: PLANEJAMENTO"): gera um
//    plano técnico detalhado em blocos (com contexto acumulado), registrando
//    cada parte como comentário e fazendo handoff in_review.
//
// Limites (instruções em ./instructions.md): não aprova, não conclui, não delega,
// não executa shell, não altera repositórios, não acessa credenciais além das
// injetadas. Nada é executado: entregas são comentários na issue.
//
// Env injetada pelo Paperclip (runtime): PAPERCLIP_API_URL, PAPERCLIP_API_KEY,
// PAPERCLIP_RUN_ID. Env de configuração do adaptador: HELPER_BASE, HELPER_KEY,
// HELPER_MODEL, HANDOFF_USER_ID.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const API_ENV = (process.env.PAPERCLIP_API_URL || "").replace(/\/api\/?$/, "");
// A URL pública (tailnet/VPN) pode não resolver dentro do container; a API
// local do próprio server sempre responde. Candidatos em ordem de preferência.
const API_CANDIDATES = [...new Set([API_ENV, "http://127.0.0.1:3100"].filter(Boolean))];
let API = API_CANDIDATES[0];
const API_KEY = process.env.PAPERCLIP_API_KEY || "";
const RUN_ID = process.env.PAPERCLIP_RUN_ID || "";
// PAPERCLIP_TASK_ID nem sempre é injetado (buildPaperclipEnv só garante
// AGENT_ID/COMPANY_ID/API_URL): resolve por fallbacks — env alternativa ou o
// marker do scratch do run (metadata.issueId).
function resolveTaskId() {
  const direct = process.env.PAPERCLIP_TASK_ID || process.env.PAPERCLIP_ISSUE_ID || "";
  if (direct) return direct;
  const dir = process.env.PAPERCLIP_RUN_SCRATCH_DIR || process.env.PAPERCLIP_SCRATCH_DIR || "";
  if (!dir) return "";
  try {
    const marker = JSON.parse(readFileSync(join(dir, ".paperclip-run-scratch.json"), "utf8"));
    return marker?.metadata?.issueId || marker?.issueId || "";
  } catch {
    return "";
  }
}
const TASK_ID = resolveTaskId();
const HELPER_BASE = process.env.HELPER_BASE || "http://litellm:4000";
const HELPER_KEY = process.env.HELPER_KEY || "";
const HELPER_MODEL = process.env.HELPER_MODEL || "medusa-local-helper";
// Review path do handoff: o produto exige um caminho de revisão válido para
// agente mover issue a in_review (human_assignee_user_id). O handoff atribui a
// issue ao responsável humano para validação da sugestão.
const HANDOFF_USER_ID = process.env.HANDOFF_USER_ID || "";

function die(msg, code = 2) {
  console.log(JSON.stringify({ event: "error", detail: msg }));
  process.exit(code);
}
function authHeaders(extra = {}) {
  return { Authorization: "Bearer " + API_KEY, "Content-Type": "application/json", ...extra };
}
async function callJson(url, options, timeoutMs = 120000) {
  try {
    const res = await fetch(url, { ...options, signal: AbortSignal.timeout(timeoutMs) });
    const text = await res.text();
    let body = null;
    try { body = text ? JSON.parse(text) : null; } catch { body = text; }
    return { status: res.status, body };
  } catch (err) {
    // Erro de rede (DNS/timeout): se a base atual não é a local, tenta a local.
    const local = "http://127.0.0.1:3100";
    if (url.startsWith(API) && API !== local) {
      const retry = local + url.slice(API.length);
      try {
        const res = await fetch(retry, { ...options, signal: AbortSignal.timeout(timeoutMs) });
        API = local;
        const text = await res.text();
        let body = null;
        try { body = text ? JSON.parse(text) : null; } catch { body = text; }
        return { status: res.status, body };
      } catch { /* cai no erro original */ }
    }
    throw err;
  }
}

if (!API_KEY || !TASK_ID) die("PAPERCLIP_API_KEY/PAPERCLIP_TASK_ID ausentes");

async function main() {
// 1) tarefa atribuída
const issue = (await callJson(`${API}/api/issues/${TASK_ID}`, { headers: authHeaders() })).body;
if (!issue || !issue.title) die("tarefa não encontrada: " + TASK_ID);
const taskText = `Título: ${issue.title}\n\nDescrição:\n${issue.description || "(sem descrição)"}`;
console.log(JSON.stringify({ event: "task", id: TASK_ID, title: issue.title }));

const here = dirname(fileURLToPath(import.meta.url));
const MODO_PLANO = String(issue.description || "").includes("MODO: PLANEJAMENTO");

// ————— MODO PLANEJAMENTO: plano técnico detalhado em blocos —————
if (MODO_PLANO) {
  const policy = readFileSync(join(here, "planning-policy.md"), "utf8");
  // Itens do formato da primeira resposta (seção 19 do prompt oficial), em blocos.
  const BLOCOS = [[1, 3], [4, 6], [7, 9], [10, 12], [13, 15], [16, 18], [19, 21], [22, 24], [25, 27]];
  const partes = [];
  for (const [de, ate] of BLOCOS) {
    // Contexto de 16K do auxiliar: acumula só a PARTE ANTERIOR (coerência local)
    // + a lista dos itens já entregues. O prompt completo já está no taskText.
    const anteriores = partes.length
      ? "\n\nPARTE ANTERIOR DO PLANO (coerência; não repita):\n\n" + partes[partes.length - 1] +
        "\n\nITENS JÁ ENTREGUES: " + partes.map((_, i) => BLOCOS[i].join("-")).join(", ")
      : "";
    const user = taskText + anteriores + `\n\n=== TAREFA DESTA PARTE ===\nEscreva SOMENTE os itens ${de} a ${ate} do formato de primeira resposta (seção 19 do prompt oficial), na ordem, com detalhamento máximo e evidências. Não escreva outros itens.`;
    const llm = await callJson(HELPER_BASE + "/v1/chat/completions", {
      method: "POST",
      headers: authHeaders({ Authorization: "Bearer " + HELPER_KEY }),
      body: JSON.stringify({
        model: HELPER_MODEL,
        messages: [{ role: "system", content: policy }, { role: "user", content: user }],
        temperature: 0.2, max_tokens: 1500,
        chat_template_kwargs: { enable_thinking: false },
      }),
    }, 300000);
    const msg = llm.body?.choices?.[0]?.message || {};
    const raw = (msg.content || "").trim();
    if (llm.status !== 200 || !raw) die(`auxiliar falhou no bloco ${de}-${ate}: ` + llm.status + " " + JSON.stringify(msg).slice(0, 120), 3);
    partes.push(raw);
    const comentario = `## Plano Medusa + Open WebUI — parte ${partes.length}/${BLOCOS.length} (itens ${de}–${ate})\n\n_(gerado pelo auxiliar local Qwen3 8B — conteúdo de PLANEJAMENTO, não execução)_\n\n${raw}`;
    const c = await callJson(`${API}/api/issues/${TASK_ID}/comments`, {
      method: "POST",
      headers: authHeaders({ "X-Paperclip-Run-Id": RUN_ID }),
      body: JSON.stringify({ body: comentario }),
    });
    if (c.status !== 200 && c.status !== 201) die("falha ao registrar parte " + partes.length + ": " + c.status, 6);
    console.log(JSON.stringify({ event: "plano_parte", parte: partes.length, itens: `${de}-${ate}`, status: c.status }));
  }
  await handoff();
  console.log(JSON.stringify({ event: "end", modo: "planejamento", partes: partes.length }));
  process.exit(0);
}

// ————— MODO TRIAGEM (default): sugestão JSON + handoff —————
// 2) política (catálogo de agentes + limites) junto ao driver
const policy = readFileSync(join(here, "instructions.md"), "utf8");

// 3) consulta ao auxiliar local (medusa-local-helper na RX 5500)
const llmReq = {
  model: HELPER_MODEL,
  messages: [
    { role: "system", content: policy },
    { role: "user", content: taskText },
  ],
  temperature: 0.2,
  max_tokens: 900,
  chat_template_kwargs: { enable_thinking: false },
};
const llm = await callJson(HELPER_BASE + "/v1/chat/completions", {
  method: "POST",
  headers: authHeaders({ Authorization: "Bearer " + HELPER_KEY }),
  body: JSON.stringify(llmReq),
}, 300000);
const msg = llm.body?.choices?.[0]?.message || {};
const raw = (msg.content || "").trim();
if (llm.status !== 200 || !raw) die("auxiliar falhou: " + llm.status + " " + JSON.stringify(msg).slice(0, 120), 3);

// 4) extrai o JSON (tolerante a cercas/lixo)
let suggestion = null;
try {
  const t = raw.replace(/^```(json)?/, "").replace(/```$/, "").trim();
  const i = t.indexOf("{"), j = t.lastIndexOf("}");
  suggestion = JSON.parse(i >= 0 && j > i ? t.slice(i, j + 1) : t);
} catch { /* mantém null */ }
if (!suggestion) die("auxiliar não devolveu JSON válido", 4);

const catalogOk = ["Hermes CEO", "OpenCode executor", "Auxiliar local"].includes(suggestion.agente_sugerido);
console.log(JSON.stringify({ event: "suggestion", agente_sugerido: suggestion.agente_sugerido, catalogo_ok: catalogOk }));

// 5) registra a sugestão na issue (comentário) e entrega para revisão do Hermes
const comment = "## Sugestão do Chief of Staff Local (NÃO é decisão)\n\nO Hermes CEO decide. Sugestão em JSON:\n\n```json\n" +
  JSON.stringify(suggestion, null, 2) + "\n```";
const c = await callJson(`${API}/api/issues/${TASK_ID}/comments`, {
  method: "POST",
  headers: authHeaders({ "X-Paperclip-Run-Id": RUN_ID }),
  body: JSON.stringify({ body: comment }),
});
console.log(JSON.stringify({ event: "comment", status: c.status }));
if (c.status !== 200 && c.status !== 201) die("falha ao registrar sugestão: " + c.status, 6);
await handoff();
console.log(JSON.stringify({ event: "end", finished: true }));
process.exit(0);
}

// handoff in_review ao responsável (human self handoff — o run não é cancelado).
async function handoff() {
  let patch = null;
  for (let tent = 0; tent < 3; tent++) {
    const fresh = (await callJson(`${API}/api/issues/${TASK_ID}`, { headers: authHeaders() })).body;
    if (fresh?.status === "in_review") { patch = { status: 200 }; break; }
    const handoffBody = { status: "in_review" };
    if (fresh?.statusVersion !== undefined && fresh?.statusVersion !== null) handoffBody.statusVersion = fresh.statusVersion;
    if (HANDOFF_USER_ID) {
      handoffBody.assigneeUserId = HANDOFF_USER_ID;
      handoffBody.assigneeAgentId = null;
    }
    patch = await callJson(`${API}/api/issues/${TASK_ID}`, {
      method: "PATCH",
      headers: authHeaders({ "X-Paperclip-Run-Id": RUN_ID }),
      body: JSON.stringify(handoffBody),
    });
    if (patch.status === 200) break;
  }
  console.log(JSON.stringify({ event: "handoff_in_review", status: patch.status }));
  if (patch.status !== 200) die("falha no handoff in_review: " + patch.status, 7);
}

main().catch((err) => {
  die("exceção não tratada: " + (err?.stack || err?.message || String(err)), 5);
});
