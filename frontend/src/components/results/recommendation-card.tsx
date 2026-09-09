import type { ReactNode } from "react";
import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

function asString(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

function asNumber(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function formatReais(valor: number) {
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function papelLabel(papel: string | undefined) {
  if (papel === "alternativa") return "Alternativa";
  return "Recomendação";
}

interface RecommendationCardProps {
  icon: ReactNode;
  title: string;
  rows: Record<string, unknown>[];
  headline: (row: Record<string, unknown>) => string | undefined;
  detail?: (row: Record<string, unknown>) => string | undefined;
  value?: (row: Record<string, unknown>) => string | undefined;
  missingValue: string;
}

export function RecommendationCard({
  icon,
  title,
  rows,
  headline,
  detail,
  value,
  missingValue,
}: RecommendationCardProps) {
  return (
    <Card className="gap-3 py-4">
      <CardHeader className="px-4">
        <CardTitle className="flex items-center gap-2 text-sm">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 px-4">
        {rows.map((row, index) => {
          const papel = asString(row.papel);
          const preco = value?.(row);
          const fonte = asString(row.fonte_url);
          const trecho = asString(row.trecho);
          return (
            <div key={String(row.id ?? index)}>
              {index > 0 && <Separator className="mb-3" />}
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-1.5">
                  <Badge variant={papel === "alternativa" ? "outline" : "secondary"}>
                    {papelLabel(papel)}
                  </Badge>
                  {asString(row.confianca) === "baixa" && (
                    <Badge variant="outline">Conferir na fonte</Badge>
                  )}
                </div>
                <p className="text-sm font-medium">{headline(row)}</p>
                {detail?.(row) && (
                  <p className="text-xs text-muted-foreground">{detail(row)}</p>
                )}
                <p className={preco ? "text-sm font-semibold" : "text-sm text-muted-foreground"}>
                  {preco ?? missingValue}
                </p>
                {trecho && (
                  <p className="line-clamp-2 text-xs text-muted-foreground">{trecho}</p>
                )}
                {fonte && (
                  <a
                    href={fonte}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                  >
                    Conferir no site <ExternalLink className="size-3" />
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

export function vooHeadline(row: Record<string, unknown>) {
  const origem = asString(row.origem);
  const destino = asString(row.destino);
  if (origem && destino) return `${origem} → ${destino}`;
  return asString(row.resumo) ?? "Voo";
}

export function vooDetail(row: Record<string, unknown>) {
  const partes = [asString(row.companhia), asString(row.horario), asString(row.data_ida)];
  if (asString(row.data_volta)) partes.push(`volta ${asString(row.data_volta)}`);
  return partes.filter(Boolean).join(" · ") || undefined;
}

export function vooValor(row: Record<string, unknown>) {
  const preco = asNumber(row.preco);
  return preco != null ? formatReais(preco) : undefined;
}

export function hotelHeadline(row: Record<string, unknown>) {
  return asString(row.nome) ?? asString(row.resumo) ?? asString(row.destino) ?? "Hospedagem";
}

export function hotelDetail(row: Record<string, unknown>) {
  const partes = [asString(row.bairro), asString(row.data_checkin), asString(row.data_checkout)];
  return partes.filter(Boolean).join(" · ") || undefined;
}

export function hotelValor(row: Record<string, unknown>) {
  const preco = asNumber(row.preco);
  return preco != null ? formatReais(preco) : undefined;
}

export function bonusHeadline(row: Record<string, unknown>) {
  return (
    asString(row.programa) ??
    asString(row.programa_destino) ??
    asString(row.resumo) ??
    "Bônus de transferência"
  );
}

export function bonusDetail(row: Record<string, unknown>) {
  return asString(row.vigencia);
}

export function bonusValor(row: Record<string, unknown>) {
  const percentual = asNumber(row.percentual);
  return percentual != null ? `${percentual}% de bônus` : undefined;
}
