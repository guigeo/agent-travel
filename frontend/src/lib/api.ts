const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export interface ResultadoFerramenta {
  ferramenta: string;
  dados: Record<string, unknown>[];
}

export interface AgentResponse {
  texto: string;
  resultados: ResultadoFerramenta[];
}

export type StreamEvent =
  | { tipo: "tool_started"; ferramenta: string }
  | { tipo: "tool_finished"; ferramenta: string; dados: ResultadoFerramenta["dados"]; erro: boolean }
  | { tipo: "texto_final"; texto: string; resultados: ResultadoFerramenta[] };

export interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: { field: string; detail: string }[];
}

export class ApiRequestError extends Error {
  problem: ProblemDetail;

  constructor(problem: ProblemDetail) {
    super(problem.detail || problem.title);
    this.problem = problem;
    this.name = "ApiRequestError";
  }
}

export const TOOL_PROGRESS_LABELS: Record<string, string> = {
  buscar_voos: "Buscando voos…",
  buscar_hospedagem: "Buscando hospedagem…",
  montar_roteiro: "Montando roteiro…",
  calcular_orcamento: "Calculando orçamento…",
  buscar_bonus_vigente: "Buscando bônus vigentes…",
  calcular_valor_ponto: "Calculando valor dos pontos…",
};

export function progressLabel(ferramenta: string): string {
  return TOOL_PROGRESS_LABELS[ferramenta] ?? `Consultando ${ferramenta}…`;
}

export async function sendChatMessage(
  sessionId: string,
  mensagem: string,
  onEvent?: (event: StreamEvent) => void,
): Promise<AgentResponse> {
  return postMessage("/chat", sessionId, mensagem, onEvent);
}

export async function sendMilesQuery(
  sessionId: string,
  mensagem: string,
  onEvent?: (event: StreamEvent) => void,
): Promise<AgentResponse> {
  return postMessage("/miles/query", sessionId, mensagem, onEvent);
}

async function postMessage(
  path: string,
  sessionId: string,
  mensagem: string,
  onEvent?: (event: StreamEvent) => void,
): Promise<AgentResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}/${sessionId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ mensagem }),
    });
  } catch {
    throw new Error("Não foi possível conectar à API. Verifique se o backend está rodando.");
  }

  if (!res.ok) {
    const problem = (await res.json().catch(() => null)) as ProblemDetail | null;
    if (problem) throw new ApiRequestError(problem);
    throw new Error(`Erro inesperado (HTTP ${res.status}).`);
  }

  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("text/event-stream")) {
    return consumeSse(res, onEvent);
  }

  return res.json() as Promise<AgentResponse>;
}

async function consumeSse(
  res: Response,
  onEvent?: (event: StreamEvent) => void,
): Promise<AgentResponse> {
  if (!res.body) {
    return { texto: "", resultados: [] };
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalResponse: AgentResponse = { texto: "", resultados: [] };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      const event = parseSseChunk(chunk);
      if (!event) continue;
      onEvent?.(event);
      if (event.tipo === "texto_final") {
        finalResponse = { texto: event.texto, resultados: event.resultados };
      }
    }
  }

  if (buffer.trim()) {
    const event = parseSseChunk(buffer);
    if (event) {
      onEvent?.(event);
      if (event.tipo === "texto_final") {
        finalResponse = { texto: event.texto, resultados: event.resultados };
      }
    }
  }

  return finalResponse;
}

function parseSseChunk(chunk: string): StreamEvent | null {
  let eventType = "";
  const dataLines: string[] = [];
  for (const line of chunk.split("\n")) {
    if (line.startsWith("event:")) {
      eventType = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trim());
    }
  }
  if (!dataLines.length) return null;
  try {
    const payload = JSON.parse(dataLines.join("\n")) as StreamEvent;
    if (eventType && payload.tipo !== eventType) {
      return { ...payload, tipo: eventType } as StreamEvent;
    }
    return payload;
  } catch {
    return null;
  }
}
