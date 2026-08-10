import { Coins, Hotel, Plane } from "lucide-react";

import type { ResultadoFerramenta } from "@/lib/api";
import { BudgetCard, type OrcamentoRow } from "@/components/results/budget-card";
import { PointsValueCard, type ValorPontoRow } from "@/components/results/points-value-card";
import { SourceListCard } from "@/components/results/source-list-card";

function meta(...values: unknown[]) {
  const text = values.filter((v): v is string => typeof v === "string" && v.length > 0).join(" → ");
  return text || undefined;
}

export function ResultRenderer({ resultado }: { resultado: ResultadoFerramenta }) {
  const { ferramenta, dados } = resultado;

  switch (ferramenta) {
    case "buscar_voos":
      return (
        <SourceListCard
          icon={<Plane className="size-4" />}
          title="Opções de voo"
          rows={dados}
          meta={(row) => meta(row.data_ida, row.data_volta)}
        />
      );

    case "buscar_hospedagem":
      return (
        <SourceListCard
          icon={<Hotel className="size-4" />}
          title="Opções de hospedagem"
          rows={dados}
          meta={(row) => meta(row.data_checkin, row.data_checkout)}
        />
      );

    case "buscar_bonus_vigente":
      return (
        <SourceListCard
          icon={<Coins className="size-4" />}
          title="Bônus de transferência vigentes"
          rows={dados}
          meta={(row) => meta(row.programa_destino)}
        />
      );

    case "calcular_orcamento":
      return <BudgetCard row={dados[0] as unknown as OrcamentoRow} />;

    case "calcular_valor_ponto":
      return <PointsValueCard row={dados[0] as unknown as ValorPontoRow} />;

    default:
      return null;
  }
}
