const SESSION_PREFIX = "agent-travel:session:";
const MESSAGES_PREFIX = "agent-travel:messages:";

export function loadSessionId(key: string): string {
  try {
    const existing = localStorage.getItem(`${SESSION_PREFIX}${key}`);
    if (existing) return existing;
  } catch {
    /* private mode */
  }
  const created = crypto.randomUUID();
  persistSessionId(key, created);
  return created;
}

export function persistSessionId(key: string, sessionId: string): void {
  try {
    localStorage.setItem(`${SESSION_PREFIX}${key}`, sessionId);
  } catch {
    /* quota / private mode */
  }
}

export function createSessionId(key: string): string {
  const sessionId = crypto.randomUUID();
  persistSessionId(key, sessionId);
  return sessionId;
}

export function loadMessages<T>(key: string): T[] {
  try {
    const raw = localStorage.getItem(`${MESSAGES_PREFIX}${key}`);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as T[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function persistMessages(key: string, messages: unknown): void {
  try {
    localStorage.setItem(`${MESSAGES_PREFIX}${key}`, JSON.stringify(messages));
  } catch {
    /* quota / private mode */
  }
}

export function clearMessages(key: string): void {
  try {
    localStorage.removeItem(`${MESSAGES_PREFIX}${key}`);
  } catch {
    /* quota / private mode */
  }
}
