import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function GraphLegend() {
    return (
        <Card className="absolute top-4 right-4 w-72 shadow-lg z-10">
            <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Legenda do Grafo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
                {/* Cores por Categoria */}
                <div>
                    <p className="font-semibold mb-2 text-muted-foreground">Cores (Categoria):</p>
                    <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-[#E11D48] border-2 border-black/20"></div>
                            <span>Suspeito</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-[#059669] border-2 border-black/20"></div>
                            <span>Testemunha</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-[#7C3AED] border-2 border-black/20"></div>
                            <span>Vítima</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-[#D97706] border-2 border-black/20"></div>
                            <span>Outro</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-[#64748B] border-2 border-black/20"></div>
                            <span>Sem Categoria</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-[#F43F5E]"></div>
                            <span>IP</span>
                        </div>
                    </div>
                </div>

                {/* Bordas Especiais */}
                <div className="border-t pt-3">
                    <p className="font-semibold mb-2 text-muted-foreground">Destaques:</p>
                    <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-[#64748B] border-[3px] border-[#FBBF24]"></div>
                            <span>Alvo/Suspeito Principal</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded-full bg-[#64748B] border-2 border-[#F59E0B]"></div>
                            <span>Conectado a Alvo</span>
                        </div>
                    </div>
                </div>

                {/* Tamanho */}
                <div className="border-t pt-3">
                    <p className="font-semibold mb-2 text-muted-foreground">Tamanho:</p>
                    <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-full bg-[#3B82F6]"></div>
                            <div className="w-3 h-3 rounded-full bg-[#3B82F6]"></div>
                            <div className="w-4 h-4 rounded-full bg-[#3B82F6]"></div>
                        </div>
                        <span>Proporcional ao nº de mensagens</span>
                    </div>
                </div>

                {/* Interação */}
                <div className="border-t pt-3">
                    <p className="font-semibold mb-2 text-muted-foreground">Interação:</p>
                    <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                            <span className="text-primary">🖱️</span>
                            <span>Duplo-clique: Editar telefone</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-primary">👆</span>
                            <span>Hover: Destacar conexões</span>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
