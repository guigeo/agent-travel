import { Clipboard, MapPinned, Plane, Send, Wallet } from "lucide-react";
import { toast } from "sonner";

import { sharedTripUrl, type TripItem, type TripPlan } from "@/lib/trip";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TripPlanCardProps {
  plan: TripPlan;
  onOpenMiles: () => void;
}

function itemDetail(item: TripItem): string {
  const data = item.dados;
  if (item.tipo === "voo") return [data.origem, data.destino, data.data_ida].filter(Boolean).join(" · ");
  if (item.tipo === "hospedagem") return [data.bairro, data.data_checkin, data.data_checkout].filter(Boolean).join(" · ");
  if (item.tipo === "roteiro") return `${Array.isArray(data.dias) ? data.dias.length : 0} dia(s) planejado(s)`;
  if (item.tipo === "orcamento") return typeof data.total_estimado === "number" ? data.total_estimado.toLocaleString("pt-BR", { style: "currency", currency: "BRL" }) : "Custo a confirmar";
  return "";
}

function itemIcon(type: TripItem["tipo"]) {
  if (type === "voo") return <Plane className="size-3.5" />;
  if (type === "orcamento") return <Wallet className="size-3.5" />;
  return <MapPinned className="size-3.5" />;
}

export function TripPlanCard({ plan, onOpenMiles }: TripPlanCardProps) {
  if (plan.itens.length === 0) return null;

  async function share() {
    const url = sharedTripUrl(plan);
    try {
      if (navigator.share) {
        await navigator.share({ title: "Minha viagem", text: "Confira meu plano de viagem", url });
      } else {
        await navigator.clipboard.writeText(url);
        toast.success("Link da viagem copiado.");
      }
    } catch {
      /* user cancelled sharing */
    }
  }

  return (
    <Card className="gap-3 border-primary/20 bg-primary/[0.03] py-4">
      <CardHeader className="px-4">
        <CardTitle className="flex items-center gap-2 text-sm">
          <MapPinned className="size-4 text-primary" />
          Minha viagem{plan.briefing.destino ? `: ${plan.briefing.destino}` : ""}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 px-4">
        <div className="space-y-2">
          {plan.itens.map((item) => (
            <div key={item.tipo} className="flex items-center gap-2 text-sm">
              <span className="text-primary">{itemIcon(item.tipo)}</span>
              <span className="font-medium">{item.titulo}</span>
              <span className="min-w-0 truncate text-xs text-muted-foreground">{itemDetail(item)}</span>
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" size="sm" variant="outline" onClick={() => void share()}>
            <Send /> Compartilhar
          </Button>
          <Button type="button" size="sm" variant="outline" onClick={onOpenMiles}>
            <Clipboard /> Ver milhas
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
