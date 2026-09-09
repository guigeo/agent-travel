import { Coins, Hotel, Plane } from "lucide-react";

import type { ResultadoFerramenta } from "@/lib/api";
import { BudgetCard, type OrcamentoRow } from "@/components/results/budget-card";
import { ItineraryCard, type RoteiroRow } from "@/components/results/itinerary-card";
import { PointsValueCard, type ValorPontoRow } from "@/components/results/points-value-card";
import {
  RecommendationCard,
  bonusDetail,
  bonusHeadline,
  bonusValor,
  hotelDetail,
  hotelHeadline,
  hotelValor,
  vooDetail,
  vooHeadline,
  vooValor,
} from "@/components/results/recommendation-card";

export function ResultRenderer({ resultado }: { resultado: ResultadoFerramenta }) {
  const { ferramenta, dados } = resultado;

  switch (ferramenta) {
    case "buscar_voos":
      return (
        <RecommendationCard
          icon={<Plane className="size-4" />}
          title="Recomendação de voo"
          rows={dados}
          headline={vooHeadline}
          detail={vooDetail}
          value={vooValor}
          missingValue="Preço a confirmar no site"
        />
      );

    case "buscar_hospedagem":
      return (
        <RecommendationCard
          icon={<Hotel className="size-4" />}
          title="Recomendação de hospedagem"
          rows={dados}
          headline={hotelHeadline}
          detail={hotelDetail}
          value={hotelValor}
          missingValue="Preço a confirmar no site"
        />
      );

    case "buscar_bonus_vigente":
      return (
        <RecommendationCard
          icon={<Coins className="size-4" />}
          title="Recomendação de bônus"
          rows={dados}
          headline={bonusHeadline}
          detail={bonusDetail}
          value={bonusValor}
          missingValue="Percentual a confirmar na fonte"
        />
      );

    case "calcular_orcamento":
      return <BudgetCard row={dados[0] as unknown as OrcamentoRow} />;

    case "calcular_valor_ponto":
      return <PointsValueCard row={dados[0] as unknown as ValorPontoRow} />;

    case "montar_roteiro":
      return <ItineraryCard row={(dados[0] ?? {}) as RoteiroRow} />;

    default:
      return null;
  }
}
