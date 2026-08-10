import { useMemo } from "react";
import { Coins, Plane } from "lucide-react";

import { sendChatMessage, sendMilesQuery } from "@/lib/api";
import { ChatPanel } from "@/components/chat-panel";
import { ModeToggle } from "@/components/mode-toggle";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Toaster } from "@/components/ui/sonner";

function useSessionId() {
  return useMemo(() => crypto.randomUUID(), []);
}

function App() {
  const chatSessionId = useSessionId();
  const milesSessionId = useSessionId();

  return (
    <div className="min-h-svh bg-background text-foreground">
      <div className="mx-auto flex min-h-svh w-full max-w-3xl flex-col gap-6 px-4 py-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Agente de Viagem</h1>
            <p className="text-sm text-muted-foreground">
              Assistente de planejamento de viagens e milhas
            </p>
          </div>
          <ModeToggle />
        </header>

        <Tabs defaultValue="planejador" className="flex-1">
          <TabsList className="w-full">
            <TabsTrigger value="planejador" className="gap-1.5">
              <Plane className="size-4" />
              Planejador de viagem
            </TabsTrigger>
            <TabsTrigger value="milhas" className="gap-1.5">
              <Coins className="size-4" />
              Agente de Milhas
            </TabsTrigger>
          </TabsList>

          <TabsContent value="planejador" className="mt-4">
            <ChatPanel
              sessionId={chatSessionId}
              onSend={sendChatMessage}
              placeholder="Ex: quero ir de São Paulo ao Rio em 2026-09-10, orçamento R$1500"
              agentLabel="o Planejador de viagem"
              agentIcon={<Plane className="size-4" />}
              emptyTitle="Vamos planejar sua próxima viagem?"
              emptyDescription="Conte destino, datas e orçamento — eu cuido de voos, hospedagem, roteiro e orçamento."
              suggestions={[
                "Quero ir de São Paulo ao Rio em 10/09, orçamento R$1500",
                "Roteiro de 5 dias em Lisboa gastando pouco",
              ]}
            />
          </TabsContent>

          <TabsContent value="milhas" className="mt-4">
            <ChatPanel
              sessionId={milesSessionId}
              onSend={sendMilesQuery}
              placeholder="Ex: vale a pena trocar meus pontos Itaú agora?"
              agentLabel="o Agente de Milhas"
              agentIcon={<Coins className="size-4" />}
              emptyTitle="Vale a pena trocar seus pontos agora?"
              emptyDescription="Independente de qualquer viagem em planejamento — pergunte sobre bônus vigentes e valor por ponto."
              suggestions={[
                "Vale a pena trocar meus pontos Itaú agora?",
                "Tenho 50 mil pontos, qual o melhor programa hoje?",
              ]}
            />
          </TabsContent>
        </Tabs>

        <footer className="text-center text-xs text-muted-foreground">
          As recomendações são apenas sugestões — finalize compras sempre no site oficial.
        </footer>
      </div>
      <Toaster />
    </div>
  );
}

export default App;
