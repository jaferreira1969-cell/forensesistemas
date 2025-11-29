import { useState, useEffect } from 'react';
import { getOperacoes, createOperacao, Operacao, getImportedFiles, ArquivoImportado } from '@/services/api';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload as UploadIcon, FileText } from 'lucide-react';
import { useToast } from '@/contexts/ToastContext';

export default function Upload() {
    const [operacoes, setOperacoes] = useState<Operacao[]>([]);
    const [selectedOp, setSelectedOp] = useState<string>('');
    const [newOpName, setNewOpName] = useState('');
    const [files, setFiles] = useState<FileList | null>(null);
    const [uploading, setUploading] = useState(false);
    const [importedFiles, setImportedFiles] = useState<ArquivoImportado[]>([]);
    const { addToast } = useToast();

    useEffect(() => {
        loadOperacoes();
    }, []);

    useEffect(() => {
        if (selectedOp) {
            loadImportedFiles();
        }
    }, [selectedOp]);

    const loadOperacoes = async () => {
        try {
            const data = await getOperacoes();
            setOperacoes(data);
        } catch (error) {
            console.error("Erro ao carregar operações", error);
            addToast("Erro ao carregar operações", 'error');
        }
    };

    const loadImportedFiles = async () => {
        if (!selectedOp) return;
        try {
            const data = await getImportedFiles(Number(selectedOp));
            setImportedFiles(data);
        } catch (error) {
            console.error("Erro ao carregar arquivos importados", error);
        }
    };

    const handleCreateOp = async () => {
        if (!newOpName) return;

        // Frontend check
        if (operacoes.some(op => op.nome.toLowerCase() === newOpName.toLowerCase())) {
            addToast("Erro: Já existe uma operação com este nome.", 'error');
            return;
        }

        try {
            const newOp = await createOperacao(newOpName);
            setOperacoes([...operacoes, newOp]);
            setSelectedOp(newOp.id.toString());
            setNewOpName('');
            addToast("Operação criada com sucesso!", 'success');
        } catch (error: any) {
            console.error("Erro ao criar operação", error);
            addToast(`Erro: ${error.response?.data?.detail || "Falha ao criar operação"}`, 'error');
        }
    };

    const handleUpload = async () => {
        if (!selectedOp || !files || files.length === 0) {
            addToast("Selecione uma operação e arquivos.", 'warning');
            return;
        }

        setUploading(true);
        addToast("Enviando e processando arquivos...", 'info');

        const formData = new FormData();
        formData.append('operacao_id', selectedOp);
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await api.post('/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            addToast(response.data.message, 'success');
            setFiles(null);
            // Recarregar lista de arquivos
            loadImportedFiles();
        } catch (error: any) {
            console.error("Erro no upload", error);
            addToast(`Erro: ${error.response?.data?.detail || error.message}`, 'error');
        } finally {
            setUploading(false);
        }
    };

    // Helper para converter UTC para UTC-3 (Brasília)
    const formatDateUTC3 = (dateString: string) => {
        try {
            // Assume que a string vem como "YYYY-MM-DD HH:MM:SS" (UTC)
            const date = new Date(dateString + " UTC");

            // Formatar para pt-BR com fuso horário de Brasília
            return new Intl.DateTimeFormat('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZone: 'America/Sao_Paulo'
            }).format(date);
        } catch (e) {
            return dateString;
        }
    };

    return (
        <div className="p-6 space-y-6 max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight">Importar Dados</h2>

            <Card>
                <CardHeader>
                    <CardTitle>1. Selecionar ou Criar Operação</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex gap-4">
                        <select
                            className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            value={selectedOp}
                            onChange={(e) => setSelectedOp(e.target.value)}
                        >
                            <option value="">Selecione uma operação...</option>
                            {operacoes.map(op => (
                                <option key={op.id} value={op.id}>{op.nome}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex gap-2 items-center">
                        <span className="text-sm text-muted-foreground">Ou criar nova:</span>
                        <input
                            type="text"
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            placeholder="Nome da Nova Operação"
                            value={newOpName}
                            onChange={(e) => setNewOpName(e.target.value)}
                        />
                        <button
                            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                            onClick={handleCreateOp}
                            disabled={!newOpName}
                        >
                            Criar
                        </button>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <UploadIcon className="w-5 h-5" />
                        2. Upload de Arquivos (HTML ou PDF)
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid w-full max-w-sm items-center gap-1.5">
                        <input
                            id="file"
                            type="file"
                            multiple
                            accept=".html,.htm,.pdf"
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            onChange={(e) => setFiles(e.target.files)}
                        />
                    </div>

                    <button
                        className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full"
                        onClick={handleUpload}
                        disabled={uploading || !selectedOp || !files}
                    >
                        {uploading ? 'Processando...' : 'Iniciar Importação'}
                    </button>
                </CardContent>
            </Card>

            {/* Grid de Arquivos Importados */}
            {selectedOp && importedFiles.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <FileText className="w-5 h-5" />
                            Arquivos Importados
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-border">
                                        <th className="text-left p-3 font-medium">Arquivo</th>
                                        <th className="text-left p-3 font-medium">Alvo</th>
                                        <th className="text-left p-3 font-medium">Período (Brasília)</th>
                                        <th className="text-left p-3 font-medium">Data Upload</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {importedFiles.map(file => (
                                        <tr key={file.id} className="border-b border-border hover:bg-muted/50 transition-colors">
                                            <td className="p-3">
                                                <span className="font-mono text-xs">{file.nome}</span>
                                            </td>
                                            <td className="p-3">
                                                <span className="font-semibold text-primary">
                                                    {file.alvo_numero || 'N/A'}
                                                </span>
                                            </td>
                                            <td className="p-3">
                                                {file.periodo_inicio && file.periodo_fim ? (
                                                    <div className="text-xs">
                                                        <div>{formatDateUTC3(file.periodo_inicio)}</div>
                                                        <div className="text-muted-foreground">até</div>
                                                        <div>{formatDateUTC3(file.periodo_fim)}</div>
                                                    </div>
                                                ) : (
                                                    <span className="text-muted-foreground">N/A</span>
                                                )}
                                            </td>
                                            <td className="p-3 text-muted-foreground">
                                                {file.data_upload}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
