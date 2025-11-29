import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface TopInterlocutor {
    numero: string;
    total: number;
}

interface TopInterlocutorsProps {
    data: TopInterlocutor[];
}

export function TopInterlocutors({ data }: TopInterlocutorsProps) {
    const maxTotal = Math.max(...data.map(d => d.total), 1);

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                    🏆 Top 5 Interlocutores
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {data.map((item, index) => (
                        <div key={index} className="space-y-1">
                            <div className="flex justify-between text-sm">
                                <span className="font-medium">{item.numero}</span>
                                <span className="text-muted-foreground">{item.total} msgs</span>
                            </div>
                            <div className="h-2 bg-secondary rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary transition-all duration-500 ease-out"
                                    style={{ width: `${(item.total / maxTotal) * 100}%` }}
                                />
                            </div>
                        </div>
                    ))}
                    {data.length === 0 && (
                        <div className="text-center text-muted-foreground py-4">
                            Nenhum dado disponível
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
