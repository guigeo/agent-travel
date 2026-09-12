import { useState, type FormEvent } from "react";
import { Compass } from "lucide-react";

import type { TripBrief } from "@/lib/trip";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface TripBriefFormProps {
  onSubmit: (message: string, brief: TripBrief) => void;
}

export function TripBriefForm({ onSubmit }: TripBriefFormProps) {
  const [brief, setBrief] = useState<TripBrief>({ viajantes: 1 });

  function update<K extends keyof TripBrief>(key: K, value: TripBrief[K]) {
    setBrief((current) => ({ ...current, [key]: value }));
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!brief.destino?.trim()) return;
    const partes = [
      `Quero planejar uma viagem para ${brief.destino.trim()}.`,
      brief.origem?.trim() && `Saindo de ${brief.origem.trim()}.`,
      brief.dataIda && `Ida em ${brief.dataIda}.`,
      brief.dataVolta && `Volta em ${brief.dataVolta}.`,
      brief.viajantes && `${brief.viajantes} viajante(s).`,
      brief.orcamento && `Orçamento total de R$ ${brief.orcamento}.`,
      brief.estilo?.trim() && `Estilo: ${brief.estilo.trim()}.`,
      brief.interesses?.trim() && `Interesses: ${brief.interesses.trim()}.`,
      "Pesquise voo e hospedagem, monte um roteiro e consolide o orçamento com fontes.",
    ].filter(Boolean);
    onSubmit(partes.join(" "), brief);
  }

  return (
    <form onSubmit={submit} className="w-full max-w-xl space-y-3 rounded-lg border bg-background p-4 text-left">
      <div className="flex items-center gap-2 text-sm font-medium">
        <Compass className="size-4 text-primary" />
        Comece com o essencial
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        <Input placeholder="Destino*" value={brief.destino ?? ""} onChange={(event) => update("destino", event.target.value)} />
        <Input placeholder="De onde você sai" value={brief.origem ?? ""} onChange={(event) => update("origem", event.target.value)} />
        <Input type="date" aria-label="Data de ida" value={brief.dataIda ?? ""} onChange={(event) => update("dataIda", event.target.value)} />
        <Input type="date" aria-label="Data de volta" value={brief.dataVolta ?? ""} onChange={(event) => update("dataVolta", event.target.value)} />
        <Input type="number" min="1" max="20" aria-label="Viajantes" placeholder="Viajantes" value={brief.viajantes ?? ""} onChange={(event) => update("viajantes", Number(event.target.value) || undefined)} />
        <Input type="number" min="0" aria-label="Orçamento total" placeholder="Orçamento total (R$)" value={brief.orcamento ?? ""} onChange={(event) => update("orcamento", Number(event.target.value) || undefined)} />
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        <Input placeholder="Estilo: econômico, romântico…" value={brief.estilo ?? ""} onChange={(event) => update("estilo", event.target.value)} />
        <Input placeholder="Interesses: comida, museus…" value={brief.interesses ?? ""} onChange={(event) => update("interesses", event.target.value)} />
      </div>
      <Button type="submit" size="sm" disabled={!brief.destino?.trim()}>
        Criar meu plano
      </Button>
    </form>
  );
}
