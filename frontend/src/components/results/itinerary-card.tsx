import { ExternalLink, MapPin, Plus } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

interface DiaRoteiro {
  dia?: unknown;
  atividades?: unknown;
}

export interface RoteiroRow {
  destino?: unknown;
  dias?: unknown;
}

export function ItineraryCard({ row, onAdd }: { row: RoteiroRow; onAdd?: () => void }) {
  const destino = typeof row.destino === "string" ? row.destino : undefined;
  const dias = Array.isArray(row.dias) ? (row.dias as DiaRoteiro[]) : [];

  return (
    <Card className="gap-3 py-4">
      <CardHeader className="px-4">
        <CardTitle className="flex items-center gap-2 text-sm">
          <MapPin className="size-4" />
          {destino ? `Roteiro em ${destino}` : "Roteiro"}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 px-4">
        {dias.map((dia, index) => {
          const numero = typeof dia.dia === "number" ? dia.dia : index + 1;
          const atividades = Array.isArray(dia.atividades)
            ? dia.atividades.filter((item): item is string => typeof item === "string")
            : [];
          return (
            <div key={`${numero}-${index}`}>
              {index > 0 && <Separator className="mb-3" />}
              <p className="text-xs font-medium text-muted-foreground">Dia {numero}</p>
              <ul className="mt-1 list-disc space-y-1 pl-4 text-sm">
                {atividades.map((atividade, atividadeIndex) => (
                  <li key={`${numero}-${atividadeIndex}`}>
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${atividade} ${destino ?? ""}`)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 hover:text-primary hover:underline"
                    >
                      {atividade} <ExternalLink className="size-3" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
        {onAdd && (
          <Button type="button" variant="outline" size="sm" className="w-fit" onClick={onAdd}>
            <Plus /> Adicionar à viagem
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
