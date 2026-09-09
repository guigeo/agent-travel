import { AlertTriangle, CheckCircle2, Wallet } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface ItemCusto {
  descricao: string;
  valor: number;
}

export interface OrcamentoRow {
  itens: ItemCusto[];
  itens_a_confirmar?: { descricao: string }[];
  total_estimado: number;
  orcamento_maximo: number | null;
  estourou_orcamento: boolean;
  parcial?: boolean;
}

function formatReais(valor: number) {
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function BudgetCard({ row }: { row: OrcamentoRow }) {
  const aConfirmar = row.itens_a_confirmar ?? [];

  return (
    <Card className="gap-3 py-4">
      <CardHeader className="px-4">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Wallet className="size-4" />
          Orçamento estimado
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 px-4">
        <div className="space-y-1.5">
          {row.itens.map((item, index) => (
            <div key={`${item.descricao}-${index}`} className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{item.descricao}</span>
              <span>{formatReais(item.valor)}</span>
            </div>
          ))}
          {aConfirmar.map((item, index) => (
            <div
              key={`confirmar-${item.descricao}-${index}`}
              className="flex items-center justify-between text-sm"
            >
              <span className="text-muted-foreground">{item.descricao}</span>
              <span className="text-muted-foreground">a confirmar</span>
            </div>
          ))}
        </div>

        <Separator />

        <div className="flex items-center justify-between text-sm font-medium">
          <span>{row.parcial ? "Total parcial" : "Total estimado"}</span>
          <span>{formatReais(row.total_estimado)}</span>
        </div>

        {row.orcamento_maximo != null && (
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Orçamento máximo</span>
            <span>{formatReais(row.orcamento_maximo)}</span>
          </div>
        )}

        {row.parcial && (
          <p className="text-xs text-muted-foreground">
            Itens sem preço na fonte ficaram de fora do total.
          </p>
        )}

        {row.orcamento_maximo != null && (
          <Badge
            variant={row.estourou_orcamento ? "destructive" : "secondary"}
            className="w-fit gap-1"
          >
            {row.estourou_orcamento ? (
              <AlertTriangle className="size-3" />
            ) : (
              <CheckCircle2 className="size-3" />
            )}
            {row.estourou_orcamento ? "Orçamento estourado" : "Dentro do orçamento"}
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
