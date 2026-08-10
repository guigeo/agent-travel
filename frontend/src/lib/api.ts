const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export interface AgentResponse {
  texto: string;
  acao_ui: string[] | null;
  dados: Record<string, unknown>[] | null;
}

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

async function postMessage(path: string, sessionId: string, mensagem: string): Promise<AgentResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}/${sessionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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

  return res.json() as Promise<AgentResponse>;
}

export function sendChatMessage(sessionId: string, mensagem: string) {
  return postMessage("/chat", sessionId, mensagem);
}

export function sendMilesQuery(sessionId: string, mensagem: string) {
  return postMessage("/miles/query", sessionId, mensagem);
}
