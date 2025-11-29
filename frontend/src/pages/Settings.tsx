import { useState, useEffect } from 'react';
import { getOperacoes, deleteOperacao, updateOperacao, Operacao } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { Link } from 'react-router-dom';
import { Settings as SettingsIcon, Trash2, Edit, Save, X, Star, Shield, Users } from 'lucide-react';

const DEFAULT_OPERATION_KEY = 'default_operation_id';

export default function Settings() {
    const { user } = useAuth();
    const [operacoes, setOperacoes] = useState<Operacao[]>([]);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editNome, setEditNome] = useState('');
    const [editDescricao, setEditDescricao] = useState('');
    const [loading, setLoading] = useState(false);
    const [defaultOpId, setDefaultOpId] = useState<number | null>(null);

    useEffect(() => {
        loadOperacoes();
        // Carregar operação padrão do localStorage
        const savedDefault = localStorage.getItem(DEFAULT_OPERATION_KEY);
        if (savedDefault) {
            setDefaultOpId(Number(savedDefault));
        }
    }, []);

    const loadOperacoes = async () => {
        try {
            const data = await getOperacoes();
            setOperacoes(data);
        } catch (error) {
            console.error('Erro ao carregar operações:', error);
        }
    };

    const handleSetDefault = (id: number) => {
        localStorage.setItem(DEFAULT_OPERATION_KEY, id.toString());
        setDefaultOpId(id);
    };

    const handleDelete = async (id: number, nome: string) => {
        if (!confirm(`Tem certeza que deseja excluir a operação "${nome}"?\n\nTODOS os dados relacionados serão perdidos!`)) {
            return;
        }

        setLoading(true);
        try {
            await deleteOperacao(id);
            setOperacoes(operacoes.filter(op => op.id !== id));

            // Se era a operação padrão, remover
            if (defaultOpId === id) {
                localStorage.removeItem(DEFAULT_OPERATION_KEY);
                setDefaultOpId(null);
            }

            alert('Operação excluída com sucesso!');
        } catch (error: any) {
            console.error('Erro ao deletar:', error);
            alert('Erro ao deletar operação: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (op: Operacao) => {
        setEditingId(op.id);
        setEditNome(op.nome);
        setEditDescricao(op.descricao || '');
    };

    const handleSave = async (id: number) => {
        if (!editNome.trim()) {
            alert('O nome não pode estar vazio');
            return;
        }

        setLoading(true);
        try {
            const updated = await updateOperacao(id, {
                nome: editNome,
                descricao: editDescricao || undefined
            });
            setOperacoes(operacoes.map(op => op.id === id ? updated : op));
            setEditingId(null);
        } catch (error: any) {
            console.error('Erro ao atualizar:', error);
            alert('Erro ao atualizar operação: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        setEditingId(null);
        setEditNome('');
        setEditDescricao('');
    };

    return (
        <div className="p-6 space-y-6 pb-20">
            <div className="flex items-center gap-3">
                <SettingsIcon className="h-8 w-8 text-primary" />
                <h2 className="text-3xl font-bold tracking-tight">Configurações</h2>
            </div>

            {/* Admin Section */}
            {user?.role === 'admin' && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Shield className="h-5 w-5 text-primary" />
                            Administração
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Link
                            to="/usuarios"
                            className="flex items-center gap-4 p-4 border rounded-lg hover:bg-accent transition-colors group"
                        >
                            <div className="p-3 bg-primary/10 rounded-full group-hover:bg-primary/20 transition-colors">
                                <Users className="h-6 w-6 text-primary" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg">Gerenciar Usuários</h3>
                                <p className="text-sm text-muted-foreground">
                                    Aprovar novos cadastros, alterar permissões e gerenciar acesso ao sistema.
                                </p>
                            </div>
                        </Link>
                    </CardContent>
                </Card>
            )}

            <Card>
                <CardHeader>
                    <CardTitle>Gerenciar Operações</CardTitle>
                    <p className="text-sm text-muted-foreground">
                        Use a estrela ⭐ para definir qual operação será selecionada automaticamente em todas as telas.
                    </p>
                </CardHeader>
                <CardContent>
                    {operacoes.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            Nenhuma operação cadastrada
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {operacoes.map((op) => (
                                <div
                                    key={op.id}
                                    className={`border rounded-lg p-4 transition-colors ${defaultOpId === op.id
                                        ? 'bg-primary/5 border-primary/50'
                                        : 'hover:bg-muted/50'
                                        }`}
                                >
                                    {editingId === op.id ? (
                                        /* Modo de edição */
                                        <div className="space-y-3">
                                            <div>
                                                <label className="text-sm font-medium block mb-1">Nome</label>
                                                <input
                                                    type="text"
                                                    value={editNome}
                                                    onChange={(e) => setEditNome(e.target.value)}
                                                    className="w-full p-2 border rounded bg-background"
                                                    placeholder="Nome da operação"
                                                />
                                            </div>
                                            <div>
                                                <label className="text-sm font-medium block mb-1">Descrição</label>
                                                <textarea
                                                    value={editDescricao}
                                                    onChange={(e) => setEditDescricao(e.target.value)}
                                                    className="w-full p-2 border rounded bg-background resize-none"
                                                    rows={2}
                                                    placeholder="Descrição (opcional)"
                                                />
                                            </div>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => handleSave(op.id)}
                                                    disabled={loading}
                                                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors disabled:opacity-50"
                                                >
                                                    <Save className="h-4 w-4" />
                                                    Salvar
                                                </button>
                                                <button
                                                    onClick={handleCancel}
                                                    disabled={loading}
                                                    className="flex items-center gap-2 px-4 py-2 border rounded hover:bg-muted transition-colors"
                                                >
                                                    <X className="h-4 w-4" />
                                                    Cancelar
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        /* Modo de visualização */
                                        <div className="flex justify-between items-start gap-4">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <h3 className="text-lg font-semibold">{op.nome}</h3>
                                                    {defaultOpId === op.id && (
                                                        <span className="text-xs px-2 py-1 bg-primary text-primary-foreground rounded-full">
                                                            Padrão
                                                        </span>
                                                    )}
                                                </div>
                                                {op.descricao && (
                                                    <p className="text-sm text-muted-foreground mt-1">{op.descricao}</p>
                                                )}
                                                <p className="text-xs text-muted-foreground mt-2">
                                                    Criada em: {new Date(op.data_criacao).toLocaleDateString('pt-BR')}
                                                </p>
                                            </div>
                                            <div className="flex gap-2 flex-shrink-0">
                                                <button
                                                    onClick={() => handleSetDefault(op.id)}
                                                    disabled={loading || editingId !== null}
                                                    className={`flex items-center gap-2 px-3 py-2 border rounded transition-colors disabled:opacity-50 ${defaultOpId === op.id
                                                        ? 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-500 text-yellow-700 dark:text-yellow-400'
                                                        : 'hover:bg-muted'
                                                        }`}
                                                    title="Definir como padrão"
                                                >
                                                    <Star className={`h-4 w-4 ${defaultOpId === op.id ? 'fill-current' : ''}`} />
                                                </button>
                                                <button
                                                    onClick={() => handleEdit(op)}
                                                    disabled={loading || editingId !== null}
                                                    className="flex items-center gap-2 px-3 py-2 border rounded hover:bg-muted transition-colors disabled:opacity-50"
                                                >
                                                    <Edit className="h-4 w-4" />
                                                    Editar
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(op.id, op.nome)}
                                                    disabled={loading || editingId !== null}
                                                    className="flex items-center gap-2 px-3 py-2 border border-destructive text-destructive rounded hover:bg-destructive/10 transition-colors disabled:opacity-50"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                    Excluir
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Informações do Sistema</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Total de Operações:</span>
                            <span className="font-medium">{operacoes.length}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Operação Padrão:</span>
                            <span className="font-medium">
                                {defaultOpId ? operacoes.find(op => op.id === defaultOpId)?.nome || 'Não definida' : 'Nenhuma'}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Versão:</span>
                            <span className="font-medium">1.0.0</span>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
