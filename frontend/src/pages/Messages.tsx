import { useState, useEffect, useRef } from 'react';
import { getOperacoes, getMessages, Operacao } from '@/services/api';
import { getDefaultOperationId } from '@/utils/defaultOperation';
import { Card, CardContent } from '@/components/ui/card';
import { FilterState } from '@/components/FilterPanel';
import { ExportButton } from '@/components/ExportButton';
import { HeaderPortal } from '@/components/HeaderPortal';

export default function Messages() {
    const [operacoes, setOperacoes] = useState<Operacao[]>([]);
    const [selectedOp, setSelectedOp] = useState<string>('');
    const [messages, setMessages] = useState<any[]>([]);
    const [allMessages, setAllMessages] = useState<any[]>([]);
    const [search, setSearch] = useState('');
    const [filters, setFilters] = useState<FilterState>({});
    const [page, setPage] = useState(0);
    const [sortConfig, setSortConfig] = useState({ key: 'data_hora', direction: 'desc' });
    // const [loading, setLoading] = useState(false);
    // const [backgroundLoading, setBackgroundLoading] = useState(false);
    const limit = 100; // Aumentado de 50 para 100
    const loadingRef = useRef(false);

    useEffect(() => {
        loadOperacoes();
    }, []);

    useEffect(() => {
        if (selectedOp) {
            loadMessagesProgressive();
        }
    }, [selectedOp, page, filters, sortConfig]);

    const loadOperacoes = async () => {
        try {
            const data = await getOperacoes();
            setOperacoes(data);
            if (data.length > 0) {
                const defaultOpId = getDefaultOperationId();
                if (defaultOpId && data.some(op => op.id === Number(defaultOpId))) {
                    setSelectedOp(defaultOpId);
                } else {
                    setSelectedOp(data[0].id.toString());
                }
            }
        } catch (error) {
            console.error("Erro ao carregar operações", error);
        }
    };

    const loadMessagesProgressive = async () => {
        if (loadingRef.current) return;
        loadingRef.current = true;
        // setLoading(true);

        try {
            // 1. Carregar as primeiras 100 mensagens IMEDIATAMENTE
            const initialData = await getMessages(
                Number(selectedOp),
                page * limit,
                limit,
                search,
                sortConfig.key,
                sortConfig.direction,
                filters.dataInicio,
                filters.dataFim
            );
            setMessages(initialData);
            setAllMessages(initialData); // Define inicial
            // setLoading(false);

            // 2. Carregar o restante em BACKGROUND (para exportação)
            if (page === 0) { // Só carregar todas se estiver na primeira página
                // setBackgroundLoading(true);
                loadRemainingMessages();
            }
        } catch (error) {
            console.error("Erro ao carregar mensagens", error);
            // setLoading(false);
        } finally {
            loadingRef.current = false;
        }
    };

    const loadRemainingMessages = async () => {
        try {
            // Carregar em batches de 200 no background
            const BATCH_SIZE = 200;
            let offset = 100; // Já temos as primeiras 100
            let allData = messages.slice(); // Cópia das mensagens iniciais
            let hasMore = true;

            while (hasMore) {
                const batch = await getMessages(
                    Number(selectedOp),
                    offset,
                    BATCH_SIZE,
                    search,
                    sortConfig.key,
                    sortConfig.direction,
                    filters.dataInicio,
                    filters.dataFim
                );

                if (batch.length === 0) {
                    hasMore = false;
                } else {
                    allData = [...allData, ...batch];
                    setAllMessages(allData);
                    offset += BATCH_SIZE;

                    // Limitar a 1000 para não travar
                    if (offset >= 1000) hasMore = false;
                }
            }
        } catch (error) {
            console.error("Erro ao carregar mensagens restantes", error);
        } finally {
            // setBackgroundLoading(false);
        }
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(0);
        loadMessagesProgressive();
    };

    const handleSort = (key: string) => {
        setSortConfig(current => ({
            key,
            direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc'
        }));
    };

    const SortIcon = ({ column }: { column: string }) => {
        if (sortConfig.key !== column) return <span className="ml-1 text-muted-foreground/30">↕</span>;
        return <span className="ml-1 text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>;
    };

    // Filtros aplicados no backend (data)
    // Filtros mantidos no frontend para tipo e telefone (minor filters)
    const filteredMessages = messages.filter(msg => {
        if (filters.tipo && msg.tipo_mensagem !== filters.tipo) return false;
        if (filters.telefone && !msg.remetente?.includes(filters.telefone) && !msg.destinatario?.includes(filters.telefone)) return false;
        return true;
    });

    const exportData = allMessages.map(msg => ({
        'Data/Hora': msg.data_hora ? new Date(msg.data_hora).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }) : '-',
        'Remetente': msg.remetente || '-',
        'Destinatário': msg.destinatario || '-',
        'Alvo': msg.alvo || '-',
        'Tipo': msg.tipo_mensagem || '-',
        'IP': msg.ip_rel?.endereco || '-',
        'Porta': msg.porta || '-'
    }));

    return (
        <div className="p-6 space-y-6 h-full flex flex-col">
            <HeaderPortal>
                <div className="flex justify-between items-center w-full">
                    <h2 className="text-xl font-bold tracking-tight">Mensagens</h2>
                    <div className="flex gap-3 items-center">
                        <div className="flex items-center gap-2">
                            <label className="text-sm font-medium whitespace-nowrap">Data Início:</label>
                            <input
                                type="date"
                                value={filters.dataInicio || ''}
                                onChange={(e) => setFilters({ ...filters, dataInicio: e.target.value || undefined })}
                                className="p-1.5 border rounded bg-background text-sm"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <label className="text-sm font-medium whitespace-nowrap">Data Fim:</label>
                            <input
                                type="date"
                                value={filters.dataFim || ''}
                                onChange={(e) => setFilters({ ...filters, dataFim: e.target.value || undefined })}
                                className="p-1.5 border rounded bg-background text-sm"
                            />
                        </div>
                        <ExportButton data={exportData} filename={`mensagens-${selectedOp}`} format="csv" />
                        <ExportButton data={exportData} filename={`mensagens-${selectedOp}`} format="excel" />
                        <select
                            className="p-1.5 border rounded bg-background text-sm min-w-[150px]"
                            value={selectedOp}
                            onChange={(e) => setSelectedOp(e.target.value)}
                        >
                            {operacoes.map(op => (
                                <option key={op.id} value={op.id}>{op.nome}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </HeaderPortal>

            <div className="flex gap-4">
                <form onSubmit={handleSearch} className="flex gap-2 w-full">
                    <input
                        type="text"
                        className="flex h-10 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
                        placeholder="Pesquisar por telefone, IP ou conteúdo..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    <button
                        type="submit"
                        className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded transition-colors"
                    >
                        Buscar
                    </button>
                </form>
            </div>

            <Card className="flex-1 flex flex-col overflow-hidden">
                <CardContent className="p-0 flex-1 overflow-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs uppercase bg-muted/50 sticky top-0 select-none">
                            <tr>
                                <th className="px-4 py-2 cursor-pointer hover:bg-muted transition-colors" onClick={() => handleSort('data_hora')}>
                                    Data/Hora <SortIcon column="data_hora" />
                                </th>
                                <th className="px-4 py-2 cursor-pointer hover:bg-muted transition-colors" onClick={() => handleSort('remetente')}>
                                    Remetente <SortIcon column="remetente" />
                                </th>
                                <th className="px-4 py-2 cursor-pointer hover:bg-muted transition-colors" onClick={() => handleSort('destinatario')}>
                                    Destinatário <SortIcon column="destinatario" />
                                </th>
                                <th className="px-4 py-2 cursor-pointer hover:bg-muted transition-colors" onClick={() => handleSort('alvo')}>
                                    Alvo <SortIcon column="alvo" />
                                </th>
                                <th className="px-4 py-2 cursor-pointer hover:bg-muted transition-colors" onClick={() => handleSort('tipo_mensagem')}>
                                    Tipo <SortIcon column="tipo_mensagem" />
                                </th>
                                <th className="px-4 py-2 cursor-pointer hover:bg-muted transition-colors" onClick={() => handleSort('ip')}>
                                    IP <SortIcon column="ip" />
                                </th>
                                <th className="px-4 py-2 cursor-pointer hover:bg-muted transition-colors" onClick={() => handleSort('porta')}>
                                    Porta <SortIcon column="porta" />
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredMessages.map((msg) => (
                                <tr key={msg.id} className="border-b hover:bg-muted/50 transition-colors text-sm">
                                    <td className="px-4 py-2 whitespace-nowrap">{msg.data_hora ? new Date(msg.data_hora).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }) : '-'}</td>
                                    <td className="px-4 py-2 font-bold text-primary">{msg.remetente}</td>
                                    <td className="px-4 py-2">{msg.destinatario}</td>
                                    <td className="px-4 py-2">{msg.alvo}</td>
                                    <td className="px-4 py-2">{msg.tipo_mensagem}</td>
                                    <td className="px-4 py-2 font-mono text-xs">{msg.ip_rel?.endereco || '-'}</td>
                                    <td className="px-4 py-2">{msg.porta}</td>
                                </tr>
                            ))}
                            {filteredMessages.length === 0 && (
                                <tr>
                                    <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                                        Nenhuma mensagem encontrada.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </CardContent>
                <div className="p-4 border-t flex justify-between items-center">
                    <button
                        className="px-4 py-2 border rounded disabled:opacity-50 transition-colors hover:bg-accent"
                        disabled={page === 0}
                        onClick={() => setPage(p => p - 1)}
                    >
                        Anterior
                    </button>
                    <span>Página {page + 1} ({filteredMessages.length} registros)</span>
                    <button
                        className="px-4 py-2 border rounded disabled:opacity-50 transition-colors hover:bg-accent"
                        disabled={messages.length < limit}
                        onClick={() => setPage(p => p + 1)}
                    >
                        Próxima
                    </button>
                </div>
            </Card>
        </div>
    );
}
