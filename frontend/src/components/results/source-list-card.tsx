import type { ReactNode } from "react";
import { ExternalLink } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface SourceItem {
  resumo?: unknown;
  trecho?: unknown;
  fonte_url?: unknown;
}

interface SourceListCardProps {
  icon: ReactNode;
  title: string;
  rows: Record<string, unknown>[];
  meta?: (row: Record<string, unknown>) => string | undefined;
}

export function SourceListCard({ icon, title, rows, meta }: SourceListCardProps) {
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
          const item = row as SourceItem;
          const metaText = meta?.(row);
          return (
            <div key={String(row.id ?? index)}>
              {index > 0 && <Separator className="mb-3" />}
              <div className="space-y-1">
                {metaText && (
                  <p className="text-xs font-medium text-muted-foreground">{metaText}</p>
                )}
                {typeof item.resumo === "string" && (
                  <p className="text-sm font-medium">{item.resumo}</p>
                )}
                {typeof item.trecho === "string" && (
                  <p className="line-clamp-2 text-xs text-muted-foreground">{item.trecho}</p>
                )}
                {typeof item.fonte_url === "string" && (
                  <a
                    href={item.fonte_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                  >
                    Ver fonte <ExternalLink className="size-3" />
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
