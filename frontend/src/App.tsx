import { useEffect, useMemo, useState } from "react";
import { Coins, Plane, RotateCcw } from "lucide-react";

import { sendChatMessage, sendMilesQuery } from "@/lib/api";
import { clearMessages, createSessionId, loadSessionId } from "@/lib/session";
import {
  emptyTripPlan,
  loadTripPlan,
  persistTripPlan,
  readSharedTripPlan,
  type TripBrief,
  type TripItemKind,
} from "@/lib/trip";
import { ChatPanel } from "@/components/chat-panel";
import { ModeToggle } from "@/components/mode-toggle";
import { TripPlanCard } from "@/components/trip-plan-card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Toaster } from "@/components/ui/sonner";

function App() {
  const [chatSessionId, setChatSessionId] = useState(() => loadSessionId("planner"));
  const milesSessionId = useMemo(() => loadSessionId("miles"), []);
  const [activeTab, setActiveTab] = useState("planejador");
  const [tripPlan, setTripPlan] = useState(loadTripPlan);
  const [milesDraft, setMilesDraft] = useState("");

  useEffect(() => {
    persistTripPlan(tripPlan);
  }, [tripPlan]);

  useEffect(() => {
    const shared = readSharedTripPlan();
    if (shared) setTripPlan(shared);
  }, []);

  function updateBrief(brief: TripBrief) {
    setTripPlan((current) => ({
      ...current,
      briefing: { ...current.briefing, ...brief },
      atualizadoEm: new Date().toISOString(),
    }));
  }

  function addToTrip(tipo: TripItemKind, titulo: string, dados: Record<string, unknown>) {
    const id = typeof dados.id === "string" ? dados.id : tipo;
    setTripPlan((current) => ({
      ...current,
      itens: [
        ...current.itens.filter((item) => item.tipo !== tipo),
        { id, tipo, titulo, dados, selecionadoEm: new Date().toISOString() },
      ],
      atualizadoEm: new Date().toISOString(),
    }));
  }

  function selectedItemId(tipo: TripItemKind) {
    return tripPlan.itens.find((item) => item.tipo === tipo)?.id;
  }

  function openMiles() {
    const destino = tripPlan.briefing.destino ?? "esta viagem";
    setMilesDraft(`Quero avaliar minhas milhas para uma viagem a ${destino}. Tenho `);
    setActiveTab("milhas");
  }

  function startNewTrip() {
    clearMessages("planner");
    setTripPlan(emptyTripPlan());
    setChatSessionId(createSessionId("planner"));
  }

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

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
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
            <div className="mb-3 flex justify-end">
              <Button type="button" size="sm" variant="outline" onClick={startNewTrip}>
                <RotateCcw /> Nova viagem
              </Button>
            </div>
            <div className="mb-4">
              <TripPlanCard
                plan={tripPlan}
                onOpenMiles={openMiles}
              />
            </div>
            <ChatPanel
              key={chatSessionId}
              sessionId={chatSessionId}
              storageKey="planner"
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
              onBriefSubmit={updateBrief}
              selectedItemId={selectedItemId}
              onAddToTrip={addToTrip}
              viajantes={tripPlan.briefing.viajantes}
            />
          </TabsContent>

          <TabsContent value="milhas" className="mt-4">
            <ChatPanel
              sessionId={milesSessionId}
              storageKey="miles"
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
              draftMessage={milesDraft}
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
