import { useState, useEffect, useRef } from 'react';
import { getOperacoes, getGeneralGraph, getCommonIpsGraph, getSharedIpsGraph, Operacao } from '@/services/api';
import { getDefaultOperationId } from '@/utils/defaultOperation';
import Graph from '@/components/Graph';
import NodeEditModal from '@/components/NodeEditModal';
import IPDetailModal from '@/components/IPDetailModal';
import { GraphLegend } from '@/components/GraphLegend';
import { Card, CardContent } from '@/components/ui/card';
import { Download, Maximize2, Minimize2 } from 'lucide-react';
import cytoscape from 'cytoscape';
import { HeaderPortal } from '@/components/HeaderPortal';

export default function GraphView() {
    const [operacoes, setOperacoes] = useState<Operacao[]>([]);
    const [selectedOp, setSelectedOp] = useState<string>('');
    const [graphType, setGraphType] = useState<'general' | 'common-ips' | 'shared-ips'>('general');
    const [layout, setLayout] = useState<string>('cose');
    const [elements, setElements] = useState<{ nodes: any[], edges: any[] } | null>(null);
    const [loading, setLoading] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [selectedNode, setSelectedNode] = useState<any>(null);
    const [ipModalOpen, setIpModalOpen] = useState(false);
    const [selectedIP, setSelectedIP] = useState<any>(null);
    const [showLegend, setShowLegend] = useState(true);
    const [fullscreen, setFullscreen] = useState(false);
    const cyRef = useRef<cytoscape.Core | null>(null);

    useEffect(() => {
        loadOperacoes();
    }, []);

    useEffect(() => {
        if (selectedOp) {
            loadGraph();
        }
    }, [selectedOp, graphType]);

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

    const loadGraph = async () => {
        setLoading(true);
        try {
            let data;
            if (graphType === 'general') {
                data = await getGeneralGraph(Number(selectedOp));
            } else if (graphType === 'common-ips') {
                data = await getCommonIpsGraph(Number(selectedOp));
            } else {
                data = await getSharedIpsGraph(Number(selectedOp));
            }
            setElements(data.elements);
        } catch (error) {
            console.error("Erro ao carregar grafo", error);
        } finally {
            setLoading(false);
        }
    };

    const handleNodeClick = (nodeData: any) => {
        if (nodeData.type === 'IP') {
            // Abrir modal de detalhes do IP
            setSelectedIP(nodeData);
            setIpModalOpen(true);
        } else if (nodeData.telefone_id) {
            // Abrir modal de edição de telefone
            setSelectedNode(nodeData);
            setModalOpen(true);
        }
    };

    const handleModalClose = () => {
        setModalOpen(false);
        setSelectedNode(null);
    };

    const handleUpdate = () => {
        loadGraph(); // Recarregar grafo após atualização
    };

    const handleExport = () => {
        if (cyRef.current) {
            const png = cyRef.current.png({ full: true, scale: 2, output: 'blob' });
            const url = URL.createObjectURL(png);
            const a = document.createElement('a');
            a.href = url;
            a.download = `grafo-operacao-${selectedOp}-${new Date().toISOString().split('T')[0]}.png`;
            a.click();
            URL.revokeObjectURL(url);
        }
    };

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().then(() => {
                setFullscreen(true);
            });
        } else {
            document.exitFullscreen().then(() => {
                setFullscreen(false);
            });
        }
    };

    // Filtrar elementos por densidade (mensagens mínimas)
    // Filtrar elementos
    const [minMessages, setMinMessages] = useState(0);
    const [searchTerm, setSearchTerm] = useState('');

    const filteredElements = elements ? (() => {
        let nodes = elements.nodes;
        let edges = elements.edges;

        // 1. Filtro por Mensagens Mínimas
        nodes = nodes.filter((n: any) => {
            const total = n.data.total_mensagens || 0;
            return total >= minMessages || n.data.type === 'IP';
        });

        // 2. Filtro por Busca (Alvo/IP + Vizinhos)
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            const matchingNodes = new Set<string>();

            // Encontrar nós que dão match
            nodes.forEach((n: any) => {
                const label = (n.data.label || '').toLowerCase();
                const id = (n.data.id || '').toLowerCase();
                const ident = (n.data.identificacao || '').toLowerCase();

                if (label.includes(term) || id.includes(term) || ident.includes(term)) {
                    matchingNodes.add(n.data.id);
                }
            });

            // Se encontrou algum, incluir vizinhos
            if (matchingNodes.size > 0) {
                const nodesToShow = new Set<string>(matchingNodes);

                edges.forEach((e: any) => {
                    if (matchingNodes.has(e.data.source)) {
                        nodesToShow.add(e.data.target);
                    }
                    if (matchingNodes.has(e.data.target)) {
                        nodesToShow.add(e.data.source);
                    }
                });

                nodes = nodes.filter((n: any) => nodesToShow.has(n.data.id));
                edges = edges.filter((e: any) => nodesToShow.has(e.data.source) && nodesToShow.has(e.data.target));
            } else {
                // Se buscou e não achou nada, mostra vazio
                return { nodes: [], edges: [] };
            }
        } else {
            // Se não tem busca, filtrar arestas baseadas nos nós visíveis (minMessages)
            const visibleNodeIds = new Set(nodes.map((n: any) => n.data.id));
            edges = edges.filter((e: any) => visibleNodeIds.has(e.data.source) && visibleNodeIds.has(e.data.target));
        }

        return { nodes, edges };
    })() : null;

    return (
        <div className="p-6 space-y-6 h-full flex flex-col">
            <HeaderPortal>
                <div className="flex justify-between items-center w-full">
                    <h2 className="text-xl font-bold tracking-tight">Visualização de Grafos</h2>
                    <div className="flex gap-4 items-center">
                        <select
                            className="p-2 border rounded bg-background text-sm"
                            value={selectedOp}
                            onChange={(e) => setSelectedOp(e.target.value)}
                        >
                            {operacoes.map(op => (
                                <option key={op.id} value={op.id}>{op.nome}</option>
                            ))}
                        </select>

                        <select
                            className="p-2 border rounded bg-background text-sm"
                            value={layout}
                            onChange={(e) => setLayout(e.target.value)}
                        >
                            <option value="cose">Força (Padrão)</option>
                            <option value="circle">Circular</option>
                            <option value="concentric">Concêntrico</option>
                            <option value="breadthfirst">Hierárquico</option>
                            <option value="grid">Grade</option>
                        </select>

                        <div className="flex items-center gap-2 border rounded px-3 py-1.5 bg-background">
                            <label className="text-sm whitespace-nowrap">Msgs mín:</label>
                            <input
                                type="number"
                                min="0"
                                max="1000"
                                value={minMessages}
                                onChange={(e) => setMinMessages(Number(e.target.value))}
                                className="w-16 p-1 border rounded bg-background text-sm"
                            />
                        </div>

                        <div className="flex items-center gap-2 border rounded px-3 py-1.5 bg-background">
                            <input
                                type="text"
                                placeholder="Buscar Alvo ou IP..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-40 p-1 border rounded bg-background text-sm"
                            />
                        </div>

                        <div className="flex rounded-md shadow-sm" role="group">
                            <button
                                type="button"
                                className={`px-3 py-1.5 text-sm font-medium border rounded-l-lg ${graphType === 'general' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-accent'}`}
                                onClick={() => setGraphType('general')}
                            >
                                Geral
                            </button>
                            <button
                                type="button"
                                className={`px-3 py-1.5 text-sm font-medium border-t border-b ${graphType === 'common-ips' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-accent'}`}
                                onClick={() => setGraphType('common-ips')}
                            >
                                IPs Comuns
                            </button>
                            <button
                                type="button"
                                className={`px-3 py-1.5 text-sm font-medium border rounded-r-lg ${graphType === 'shared-ips' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-accent'}`}
                                onClick={() => setGraphType('shared-ips')}
                            >
                                IPs Compartilhados
                            </button>
                        </div>
                    </div>
                </div>
            </HeaderPortal>

            <Card className={`flex-1 flex flex-col ${fullscreen ? 'fixed inset-0 z-50 m-0 rounded-none' : ''}`}>
                <CardContent className="p-0 flex-1 relative bg-background">
                    {/* Controls Overlay */}
                    <div className="absolute top-4 left-4 z-10 flex gap-2">
                        <button
                            onClick={handleExport}
                            className="p-2 bg-background/80 backdrop-blur border rounded-md shadow-sm hover:bg-accent"
                            title="Exportar como PNG"
                        >
                            <Download className="w-4 h-4" />
                        </button>
                        <button
                            onClick={toggleFullscreen}
                            className="p-2 bg-background/80 backdrop-blur border rounded-md shadow-sm hover:bg-accent"
                            title={fullscreen ? "Sair da Tela Cheia" : "Tela Cheia"}
                        >
                            {fullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                        </button>
                        <button
                            onClick={() => setShowLegend(!showLegend)}
                            className={`p-2 border rounded-md shadow-sm hover:bg-accent ${showLegend ? 'bg-primary text-primary-foreground' : 'bg-background/80 backdrop-blur'}`}
                            title="Alternar Legenda"
                        >
                            <span className="text-xs font-bold">L</span>
                        </button>
                    </div>

                    {/* Legend Overlay */}
                    {showLegend && <GraphLegend />}

                    {loading && (
                        <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10">
                            <span>Carregando...</span>
                        </div>
                    )}
                    {filteredElements && filteredElements.nodes.length > 0 ? (
                        <Graph
                            elements={filteredElements}
                            layout={layout}
                            onNodeClick={handleNodeClick}
                            onCy={(cy) => { cyRef.current = cy; }}
                        />
                    ) : (
                        <div className="flex items-center justify-center h-full text-muted-foreground">
                            {elements && elements.nodes.length > 0
                                ? 'Nenhum nó atende aos filtros'
                                : 'Selecione uma operação para visualizar'}
                        </div>
                    )}
                </CardContent>
            </Card>

            {selectedNode && (
                <NodeEditModal
                    isOpen={modalOpen}
                    onClose={handleModalClose}
                    nodeData={selectedNode}
                    operacaoId={Number(selectedOp)}
                    onUpdate={handleUpdate}
                />
            )}

            {selectedIP && (
                <IPDetailModal
                    isOpen={ipModalOpen}
                    onClose={() => {
                        setIpModalOpen(false);
                        setSelectedIP(null);
                    }}
                    ipData={selectedIP}
                />
            )}
        </div>
    );
}
