import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { SendHorizontal, Sparkles } from "lucide-react";
import { toast } from "sonner";

import { ApiRequestError, type AgentResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
}

interface ChatPanelProps {
  sessionId: string;
  placeholder: string;
  suggestions: string[];
  emptyTitle: string;
  emptyDescription: string;
  agentIcon: ReactNode;
  agentLabel: string;
  onSend: (sessionId: string, mensagem: string) => Promise<AgentResponse>;
}

function newId() {
  return crypto.randomUUID();
}

export function ChatPanel({
  sessionId,
  placeholder,
  suggestions,
  emptyTitle,
  emptyDescription,
  agentIcon,
  agentLabel,
  onSend,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  async function submit(mensagem: string) {
    const trimmed = mensagem.trim();
    if (!trimmed || isSending) return;

    setMessages((prev) => [...prev, { id: newId(), role: "user", text: trimmed }]);
    setInput("");
    setIsSending(true);

    try {
      const response = await onSend(sessionId, trimmed);
      setMessages((prev) => [...prev, { id: newId(), role: "assistant", text: response.texto }]);
    } catch (err) {
      const message =
        err instanceof ApiRequestError
          ? err.problem.detail || err.problem.title
          : err instanceof Error
            ? err.message
            : "Erro inesperado.";
      toast.error(message);
    } finally {
      setIsSending(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    void submit(input);
  }

  return (
    <div className="flex h-[65vh] flex-col overflow-hidden rounded-xl border bg-card">
      <ScrollArea className="min-h-0 flex-1 px-4">
        <div className="flex flex-col gap-4 py-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center gap-4 rounded-lg border border-dashed py-12 text-center">
              <div className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                {agentIcon}
              </div>
              <div className="space-y-1">
                <p className="font-medium">{emptyTitle}</p>
                <p className="text-sm text-muted-foreground">{emptyDescription}</p>
              </div>
              <div className="flex flex-wrap justify-center gap-2 px-4">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => void submit(suggestion)}
                    className="rounded-full border px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-primary hover:text-primary"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex items-start gap-3",
                message.role === "user" && "flex-row-reverse",
              )}
            >
              <Avatar className="mt-0.5 size-8 shrink-0">
                <AvatarFallback
                  className={cn(
                    message.role === "assistant" && "bg-primary/10 text-primary",
                  )}
                >
                  {message.role === "user" ? "V" : agentIcon}
                </AvatarFallback>
              </Avatar>
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                  message.role === "user"
                    ? "rounded-tr-sm bg-primary text-primary-foreground"
                    : "rounded-tl-sm bg-muted",
                )}
              >
                {message.role === "assistant" ? (
                  <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1.5 prose-ul:my-1.5 prose-ol:my-1.5">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{message.text}</p>
                )}
              </div>
            </div>
          ))}

          {isSending && (
            <div className="flex items-start gap-3">
              <Avatar className="mt-0.5 size-8 shrink-0">
                <AvatarFallback className="bg-primary/10 text-primary">{agentIcon}</AvatarFallback>
              </Avatar>
              <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-muted px-4 py-3">
                <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.3s]" />
                <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.15s]" />
                <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground/60" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t p-3">
        <Sparkles className="size-4 shrink-0 text-muted-foreground" aria-hidden />
        <Input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder={placeholder}
          disabled={isSending}
          aria-label={`Mensagem para ${agentLabel}`}
          className="border-0 shadow-none focus-visible:ring-0"
        />
        <Button type="submit" size="icon" disabled={isSending || !input.trim()}>
          <SendHorizontal className="size-4" />
          <span className="sr-only">Enviar</span>
        </Button>
      </form>
    </div>
  );
}
