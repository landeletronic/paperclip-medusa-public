// agent-run.mjs — driver de agente para container efêmero por run (Fase 4, F4.2).
//
// Executa uma tarefa real de agente: loop de raciocínio + ferramentas contra o
// LiteLLM LOCAL (OpenAI-compatible), com inferência 100% local. Roda DENTRO do
// container criado pelo executor (contrato F1.1/F1.2) — o `paperclip` nunca vê
// docker.sock; este processo só enxerga o workspace montado em /workspace.
//
// Ferramentas: read_file, list_files, write_file (todas confinadas a /workspace)
// e finish (conclui a tarefa). Saída: transcrição no stdout + artefato no
// workspace (as ferramentas write_file gravam no workspace persistente).
//
// Env: AGENT_API_KEY (chave virtual por run), LITELLM_BASE, AGENT_MODEL, AGENT_TASK.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { resolve, dirname, relative, join } from "node:path";

const BASE = process.env.LITELLM_BASE || "http://litellm:4000";
const MODEL = process.env.AGENT_MODEL || "medusa-primary";
const API_KEY = process.env.AGENT_API_KEY || "";
const TASK = process.env.AGENT_TASK || "Produza /workspace/artifacts/relatorio.md.";
const WS = "/workspace";
const MAX_TURNS = 8;

if (!API_KEY) {
  console.log(JSON.stringify({ event: "error", detail: "AGENT_API_KEY ausente" }));
  process.exit(2);
}

const TOOLS = [
  { type: "function", function: { name: "read_file", description: "Lê um arquivo do workspace (/workspace)",
    parameters: { type: "object", properties: { path: { type: "string", description: "caminho relativo a /workspace" } }, required: ["path"] } } },
  { type: "function", function: { name: "list_files", description: "Lista arquivos de um diretório do workspace",
    parameters: { type: "object", properties: { path: { type: "string", description: "diretório relativo a /workspace (vazio = raiz)" } } } } },
  { type: "function", function: { name: "write_file", description: "Escreve um arquivo no workspace (cria diretórios)",
    parameters: { type: "object", properties: { path: { type: "string" }, content: { type: "string" } }, required: ["path", "content"] } } },
  { type: "function", function: { name: "finish", description: "Conclui a tarefa com um resumo final",
    parameters: { type: "object", properties: { summary: { type: "string" } }, required: ["summary"] } } },
];

function safePath(p) {
  const raw = (p || "").trim();
  // caminho absoluto sob /workspace usa o próprio caminho; relativo é re-enraizado
  const abs = raw.startsWith("/") ? resolve(raw) : resolve(WS, raw);
  if (abs !== WS && !abs.startsWith(WS + "/")) throw new Error("caminho fora de /workspace: " + p);
  return abs;
}

function runTool(name, args) {
  try {
    if (name === "read_file") {
      const abs = safePath(args.path);
      return readFileSync(abs, "utf8").slice(0, 20000);
    }
    if (name === "list_files") {
      const abs = args.path ? safePath(args.path) : WS;
      return readdirSync(abs).map((n) => {
        try { return statSync(join(abs, n)).isDirectory() ? n + "/" : n; } catch { return n; }
      }).join("\n") || "(vazio)";
    }
    if (name === "write_file") {
      const abs = safePath(args.path);
      mkdirSync(dirname(abs), { recursive: true });
      writeFileSync(abs, args.content ?? "");
      wroteFiles++;
      return "escrito: " + relative(WS, abs) + " (" + (args.content ?? "").length + " bytes)";
    }
    if (name === "finish") return "__FINISH__" + (args.summary || "");
    return "ferramenta desconhecida: " + name;
  } catch (e) {
    return "erro: " + e.message;
  }
}

async function chat(messages) {
  const res = await fetch(BASE + "/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + API_KEY },
    body: JSON.stringify({ model: MODEL, messages, tools: TOOLS, temperature: 0.3, max_tokens: 8192 }),
    signal: AbortSignal.timeout(180000),
  });
  if (!res.ok) throw new Error("LLM HTTP " + res.status + ": " + (await res.text()).slice(0, 200));
  return res.json();
}

const messages = [
  { role: "system", content:
    "Você é o executor de tarefas do Paperclip Medusa, rodando em um container efêmero por run. " +
    "Seu workspace persistente é /workspace: leia o material existente com as ferramentas, escreva " +
    "o artefato pedido com write_file e SÓ ENTÃO conclua com finish. Regra obrigatória: use write_file " +
    "para criar o arquivo de artefato pedido ANTES de chamar finish. Seja objetivo e cite os arquivos consultados." },
  { role: "user", content: TASK },
];

console.log(JSON.stringify({ event: "start", model: MODEL, task: TASK.slice(0, 120) }));
let finished = false;
let wroteFiles = 0;
let finishSummary = "";
for (let turn = 1; turn <= MAX_TURNS && !finished; turn++) {
  const resp = await chat(messages);
  const msg = (resp.choices?.[0]?.message) || {};
  const reasoning = (msg.reasoning_content || "").length;
  const tcs = msg.tool_calls || [];
  console.log(JSON.stringify({ event: "turn", turn, reasoning_chars: reasoning, tool_calls: tcs.map((t) => t.function?.name) }));

  if (tcs.length === 0) {
    const content = msg.content || "";
    if (content.trim() === "") {
      // raciocínio consumido sem emitir chamada: pedir continuação (não é fim)
      console.log(JSON.stringify({ event: "retry", turn, detail: "resposta vazia (racocinio cortado?); continuando" }));
      messages.push({ role: "assistant", content: "" });
      messages.push({ role: "user", content: "Continue. Use as ferramentas (write_file/finish) para concluir." });
      continue;
    }
    messages.push({ role: "assistant", content });
    console.log(JSON.stringify({ event: "final_content", preview: content.slice(0, 160) }));
    finished = true;
    break;
  }
  messages.push({ role: "assistant", content: msg.content || "", tool_calls: tcs });
  for (const tc of tcs) {
    let args = {};
    try { args = JSON.parse(tc.function?.arguments || "{}"); } catch {}
    const out = runTool(tc.function?.name, args);
    if (out.startsWith("__FINISH__")) {
      finishSummary = out.slice(10);
      console.log(JSON.stringify({ event: "finish", summary: finishSummary.slice(0, 400) }));
      finished = true;
      break;
    }
    console.log(JSON.stringify({ event: "tool", name: tc.function?.name, result: String(out).slice(0, 160) }));
    messages.push({ role: "tool", tool_call_id: tc.id, content: String(out) });
  }
}
console.log(JSON.stringify({ event: "end", finished, wrote_files: wroteFiles }));
// fallback: se o agente concluiu sem gravar artefato, o resumo final vira artefato
// (a aceitação exige artefato preservado no workspace em todo run concluído).
if (finished && wroteFiles === 0 && finishSummary.trim() !== "") {
  const fallback = join(WS, "artifacts", "relatorio-agente-" + Date.now() + ".md");
  try {
    mkdirSync(dirname(fallback), { recursive: true });
    writeFileSync(fallback, "# Relatório do agente (fallback)\n\n" + finishSummary + "\n");
    console.log(JSON.stringify({ event: "artifact_fallback", path: relative(WS, fallback) }));
  } catch (e) {
    console.log(JSON.stringify({ event: "artifact_fallback_error", detail: e.message }));
  }
}
process.exit(finished ? 0 : 3);
