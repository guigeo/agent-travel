import { Coins, Hotel, Plane } from "lucide-react";

import type { ResultadoFerramenta } from "@/lib/api";
import type { TripItemKind } from "@/lib/trip";
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

function asText(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

function linkBuscaVoo(dados: Record<string, unknown>): string | undefined {
  const existente = asText(dados.continuar_busca_url);
  if (existente) return existente;
  const origem = asText(dados.origem);
  const destino = asText(dados.destino);
  const ida = asText(dados.data_ida);
  if (!origem || !destino || !ida) return undefined;
  const volta = asText(dados.data_volta);
  const trechos = [`${origem}.${destino}.${ida}`];
  if (volta) trechos.push(`${destino}.${origem}.${volta}`);
  return `https://www.google.com/travel/flights?hl=pt-BR#flt=${trechos.join("*")};c:BRL;e:1;sd:1;t:f`;
}

function linkBuscaHospedagem(dados: Record<string, unknown>): string | undefined {
  const existente = asText(dados.continuar_busca_url);
  if (existente) return existente;
  const destino = asText(dados.destino);
  const checkin = asText(dados.data_checkin);
  const checkout = asText(dados.data_checkout);
  if (!destino || !checkin || !checkout) return undefined;
  const hospedes = typeof dados.hospedes === "number" && dados.hospedes > 0 ? dados.hospedes : 1;
  return `https://www.booking.com/searchresults.html?${new URLSearchParams({
    ss: destino,
    checkin,
    checkout,
    group_adults: String(hospedes),
    no_rooms: "1",
  })}`;
}

interface ResultRendererProps {
  resultado: ResultadoFerramenta;
  selectedItemId?: (tipo: TripItemKind) => string | undefined;
  onAddToTrip?: (tipo: TripItemKind, titulo: string, dados: Record<string, unknown>) => void;
  viajantes?: number;
}

export function ResultRenderer({
  resultado,
  selectedItemId,
  onAddToTrip,
  viajantes,
}: ResultRendererProps) {
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
          primaryActionLabel="Pesquisar no Google Flights"
          primaryActionUrl={linkBuscaVoo}
          selectedRowId={selectedItemId?.("voo")}
          onSelect={(dados) => onAddToTrip?.("voo", "Voo", dados)}
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
          primaryActionLabel="Buscar no Booking.com"
          primaryActionUrl={linkBuscaHospedagem}
          selectedRowId={selectedItemId?.("hospedagem")}
          onSelect={(dados) => onAddToTrip?.("hospedagem", "Hospedagem", dados)}
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
      return <BudgetCard row={dados[0] as unknown as OrcamentoRow} viajantes={viajantes} onAdd={() => onAddToTrip?.("orcamento", "Orçamento", dados[0] ?? {})} />;

    case "calcular_valor_ponto":
      return <PointsValueCard row={dados[0] as unknown as ValorPontoRow} />;

    case "montar_roteiro":
      return <ItineraryCard row={(dados[0] ?? {}) as RoteiroRow} onAdd={() => onAddToTrip?.("roteiro", "Roteiro", dados[0] ?? {})} />;

    default:
      return null;
  }
}
