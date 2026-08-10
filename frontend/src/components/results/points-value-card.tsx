import { TrendingUp } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface ValorPontoRow {
  milhas_resultantes: number;
  valor_estimado_reais: number;
  valor_por_ponto_centavos: number;
}

function formatReais(valor: number) {
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatNumber(valor: number) {
  return valor.toLocaleString("pt-BR");
}

export function PointsValueCard({ row }: { row: ValorPontoRow }) {
  const stats = [
    { label: "Milhas resultantes", value: formatNumber(row.milhas_resultantes) },
    { label: "Valor estimado", value: formatReais(row.valor_estimado_reais) },
    { label: "Valor por ponto", value: `${row.valor_por_ponto_centavos.toFixed(2)}¢` },
  ];

  return (
    <Card className="gap-3 py-4">
      <CardHeader className="px-4">
        <CardTitle className="flex items-center gap-2 text-sm">
          <TrendingUp className="size-4" />
          Valor da transferência
        </CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-3 gap-3 px-4">
        {stats.map((stat) => (
          <div key={stat.label} className="space-y-0.5">
            <p className="text-xs text-muted-foreground">{stat.label}</p>
            <p className="text-sm font-semibold">{stat.value}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
