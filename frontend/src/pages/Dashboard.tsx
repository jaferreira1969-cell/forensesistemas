import { useEffect, useState } from 'react';
import {
    getOperacoes, getStats, getEvolution, getMessageTypes,
    getActivityHeatmap, getTopInterlocutors, getPeakHours,
    generateIntelligenceReport,
    Operacao, Stats
} from '@/services/api';
import { useToast } from '@/contexts/ToastContext';
import { getDefaultOperationId } from '@/utils/defaultOperation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MessageTypeChart } from '@/components/charts/MessageTypeChart';
import { ActivityHeatmap } from '@/components/charts/ActivityHeatmap';
import { TopInterlocutors } from '@/components/dashboard/TopInterlocutors';
import { PeakHoursChart } from '@/components/charts/PeakHoursChart';
import { Users, MessageSquare, Globe, FileText, Download, Activity, Brain } from 'lucide-react';
import { HeaderPortal } from '@/components/HeaderPortal';

export default function Dashboard() {
    const [operacoes, setOperacoes] = useState<Operacao[]>([]);
    const [selectedOp, setSelectedOp] = useState<number | null>(null);
    const [stats, setStats] = useState<Stats | null>(null);
    const [evolution, setEvolution] = useState<any[]>([]);
    const [messageTypes, setMessageTypes] = useState<any[]>([]);
    const [heatmapData, setHeatmapData] = useState<any[]>([]);
    const [topInterlocutors, setTopInterlocutors] = useState<any[]>([]);
    const [peakHours, setPeakHours] = useState<any[]>([]);
    const [generatingReport, setGeneratingReport] = useState(false);
    const { addToast } = useToast();

    useEffect(() => {
        loadOperacoes();
    }, []);

    useEffect(() => {
        if (selectedOp) {
            loadStats(selectedOp);
            loadCharts(selectedOp);
        }
    }, [selectedOp]);

    const loadOperacoes = async () => {
        try {
            const data = await getOperacoes();
            setOperacoes(data);
            if (data.length > 0 && !selectedOp) {
                // Tentar usar operação padrão primeiro
                const defaultOpId = getDefaultOperationId();
                if (defaultOpId && data.some(op => op.id === Number(defaultOpId))) {
                    setSelectedOp(Number(defaultOpId));
                } else {
                    setSelectedOp(data[0].id);
                }
            }
        } catch (error) {
            console.error("Erro ao carregar operações", error);
        }
    };

    const loadStats = async (id: number) => {
        try {
            const s = await getStats(id);
            setStats(s);
            const e = await getEvolution(id);
            setEvolution(e);
        } catch (error) {
            console.error("Erro ao carregar estatísticas", error);
        }
    };

    const loadCharts = async (id: number) => {
        try {
            const types = await getMessageTypes(id);
            setMessageTypes(types);

            const heatmap = await getActivityHeatmap(id);
            setHeatmapData(heatmap);

            const top = await getTopInterlocutors(id);
            setTopInterlocutors(top);

            const peak = await getPeakHours(id);
            setPeakHours(peak);
        } catch (error) {
            console.error("Erro ao carregar gráficos", error);
        }
    };

    const handleGenerateReport = async () => {
        if (!selectedOp) return;

        setGeneratingReport(true);
        try {
            const blob = await generateIntelligenceReport(selectedOp);

            // Criar URL para download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Relatorio_Inteligencia_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            addToast('Relatório gerado com sucesso!', 'success');
        } catch (error) {
            console.error('Erro ao gerar relatório:', error);
            addToast('Erro ao gerar relatório de inteligência', 'error');
        } finally {
            setGeneratingReport(false);
        }
    };

    const handleExportPDF = async () => {
        if (!selectedOp) return;
        try {
            const blob = await import('@/services/api').then(m => m.exportPDF(selectedOp));
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `relatorio_operacao_${selectedOp}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Erro ao exportar PDF", error);
            alert("Erro ao gerar relatório PDF");
        }
    };

    return (
        <div className="p-6 space-y-6 pb-20">
            <HeaderPortal>
                <div className="flex justify-between items-center w-full">
                    <div className="flex items-center gap-3">
                        <Activity className="h-6 w-6 text-primary" />
                        <h2 className="text-xl font-bold tracking-tight">
                            {operacoes.find(op => op.id === selectedOp)?.nome || 'Dashboard'}
                        </h2>
                    </div>
                    <div className="flex gap-4 items-center">
                        <button
                            onClick={handleGenerateReport}
                            disabled={generatingReport}
                            className="bg-blue-600 text-white hover:bg-blue-700 px-3 py-1.5 rounded text-sm flex items-center gap-2 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Brain className="h-4 w-4" />
                            <span>{generatingReport ? 'Gerando...' : 'Relatório de Inteligência'}</span>
                        </button>
                        <button
                            onClick={handleExportPDF}
                            className="bg-red-600 text-white hover:bg-red-700 px-3 py-1.5 rounded text-sm flex items-center gap-2 transition-colors shadow-sm"
                        >
                            <Download className="h-4 w-4" />
                            <span>Exportar Relatório</span>
                        </button>
                        <select
                            className="p-1.5 border rounded bg-background shadow-sm min-w-[200px] text-sm"
                            value={selectedOp || ''}
                            onChange={(e) => setSelectedOp(Number(e.target.value))}
                        >
                            {operacoes.map(op => (
                                <option key={op.id} value={op.id}>{op.nome}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </HeaderPortal>

            {stats && (
                <div className="grid gap-4 md:grid-cols-3">
                    <Card className="border-l-4 border-l-blue-500 shadow-sm hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">Total de Telefones</CardTitle>
                            <Users className="h-4 w-4 text-blue-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.total_telefones}</div>
                        </CardContent>
                    </Card>
                    <Card className="border-l-4 border-l-green-500 shadow-sm hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">Total de Mensagens</CardTitle>
                            <MessageSquare className="h-4 w-4 text-green-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.total_mensagens}</div>
                        </CardContent>
                    </Card>
                    <Card className="border-l-4 border-l-purple-500 shadow-sm hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">IPs Únicos</CardTitle>
                            <Globe className="h-4 w-4 text-purple-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.total_ips}</div>
                        </CardContent>
                    </Card>
                </div>
            )}

            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-7">
                <div className="col-span-4">
                    <Card className="h-full shadow-sm">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Activity className="h-5 w-5 text-primary" />
                                Evolução Temporal
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pl-2">
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={evolution}>
                                        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" vertical={false} />
                                        <XAxis
                                            dataKey="data"
                                            className="text-xs"
                                            tickLine={false}
                                            axisLine={false}
                                        />
                                        <YAxis
                                            className="text-xs"
                                            tickLine={false}
                                            axisLine={false}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                                            itemStyle={{ color: 'hsl(var(--foreground))' }}
                                            cursor={{ fill: 'hsl(var(--muted))', opacity: 0.2 }}
                                        />
                                        <Bar dataKey="total" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="col-span-3">
                    <PeakHoursChart data={peakHours} />
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <div className="col-span-3">
                    <Card className="h-full shadow-sm">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="h-5 w-5 text-primary" />
                                Tipos de Mensagem
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {messageTypes.length > 0 ? (
                                <MessageTypeChart data={messageTypes} />
                            ) : (
                                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                                    Nenhum dado disponível
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                <div className="col-span-4">
                    <TopInterlocutors data={topInterlocutors} />
                </div>
            </div>

            <Card className="shadow-sm">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Activity className="h-5 w-5 text-primary" />
                        Mapa de Atividade (Horário vs Dia da Semana)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {heatmapData.length > 0 ? (
                        <ActivityHeatmap data={heatmapData} />
                    ) : (
                        <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                            Nenhum dado disponível
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
