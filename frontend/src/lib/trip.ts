const TRIP_STORAGE_KEY = "agent-travel:trip";

export type TripItemKind = "voo" | "hospedagem" | "roteiro" | "orcamento";

export interface TripBrief {
  origem?: string;
  destino?: string;
  dataIda?: string;
  dataVolta?: string;
  viajantes?: number;
  orcamento?: number;
  estilo?: string;
  interesses?: string;
}

export interface TripItem {
  id: string;
  tipo: TripItemKind;
  titulo: string;
  dados: Record<string, unknown>;
  selecionadoEm: string;
}

export interface TripPlan {
  briefing: TripBrief;
  itens: TripItem[];
  atualizadoEm: string;
}

export const emptyTripPlan = (): TripPlan => ({
  briefing: {},
  itens: [],
  atualizadoEm: new Date().toISOString(),
});

function isTripPlan(value: unknown): value is TripPlan {
  if (!value || typeof value !== "object") return false;
  const plan = value as Partial<TripPlan>;
  return Array.isArray(plan.itens) && Boolean(plan.briefing);
}

export function loadTripPlan(): TripPlan {
  try {
    const raw = localStorage.getItem(TRIP_STORAGE_KEY);
    if (!raw) return emptyTripPlan();
    const parsed = JSON.parse(raw) as unknown;
    return isTripPlan(parsed) ? parsed : emptyTripPlan();
  } catch {
    return emptyTripPlan();
  }
}

export function persistTripPlan(plan: TripPlan): void {
  try {
    localStorage.setItem(TRIP_STORAGE_KEY, JSON.stringify(plan));
  } catch {
    /* quota / private mode */
  }
}

export function readSharedTripPlan(): TripPlan | null {
  try {
    const hash = new URLSearchParams(window.location.hash.slice(1));
    const encoded = hash.get("viagem");
    if (!encoded) return null;
    const parsed = JSON.parse(decodeURIComponent(encoded)) as unknown;
    return isTripPlan(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export function sharedTripUrl(plan: TripPlan): string {
  const url = new URL(window.location.href);
  url.hash = new URLSearchParams({ viagem: encodeURIComponent(JSON.stringify(plan)) }).toString();
  return url.toString();
}
