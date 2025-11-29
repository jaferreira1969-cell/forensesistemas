import { useState, useEffect } from 'react';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/contexts/ToastContext';
import { Shield, Check, X, User, Edit, Trash2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface UserData {
    id: number;
    nome: string;
    email: string;
    role: string;
    status: string;
    foto?: string;
    data_criacao: string;
    ultimo_login?: string;
}

export default function AdminUsers() {
    const [users, setUsers] = useState<UserData[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingUser, setEditingUser] = useState<UserData | null>(null);
    const [editForm, setEditForm] = useState({ nome: '', email: '', role: '' });
    const { addToast } = useToast();
    const { user: currentUser } = useAuth();

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            const response = await api.get('/auth/users');
            setUsers(response.data);
        } catch (error) {
            console.error("Erro ao carregar usuários", error);
            addToast("Erro ao carregar lista de usuários", 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleStatusChange = async (userId: number, newStatus: string) => {
        try {
            await api.put(`/auth/users/${userId}/status`, { status: newStatus });
            addToast(`Status atualizado para ${newStatus}`, 'success');
            loadUsers();
        } catch (error: any) {
            console.error("Erro ao atualizar status", error);
            addToast(error.response?.data?.detail || "Erro ao atualizar status", 'error');
        }
    };

    const handleEditClick = (user: UserData) => {
        setEditingUser(user);
        setEditForm({ nome: user.nome, email: user.email, role: user.role });
    };

    const handleEditSave = async () => {
        if (!editingUser) return;

        try {
            await api.put(`/auth/users/${editingUser.id}`, editForm);
            addToast("Usuário atualizado com sucesso", 'success');
            setEditingUser(null);
            loadUsers();
        } catch (error: any) {
            console.error("Erro ao atualizar usuário", error);
            addToast(error.response?.data?.detail || "Erro ao atualizar usuário", 'error');
        }
    };

    const handleDelete = async (userId: number, userName: string) => {
        if (!confirm(`Tem certeza que deseja excluir o usuário "${userName}"?\n\nEsta ação não pode ser desfeita!`)) {
            return;
        }

        try {
            await api.delete(`/auth/users/${userId}`);
            addToast("Usuário excluído com sucesso", 'success');
            loadUsers();
        } catch (error: any) {
            console.error("Erro ao excluir usuário", error);
            addToast(error.response?.data?.detail || "Erro ao excluir usuário", 'error');
        }
    };

    if (loading) {
        return <div className="p-8 text-center">Carregando usuários...</div>;
    }

    return (
        <div className="p-6 space-y-6 max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                <Shield className="h-8 w-8 text-primary" />
                Gestão de Usuários
            </h2>

            <Card>
                <CardHeader>
                    <CardTitle>Usuários Cadastrados</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs uppercase bg-muted/50">
                                <tr>
                                    <th className="px-4 py-3">Usuário</th>
                                    <th className="px-4 py-3">Email</th>
                                    <th className="px-4 py-3">Role</th>
                                    <th className="px-4 py-3">Status</th>
                                    <th className="px-4 py-3">Criado em</th>
                                    <th className="px-4 py-3 text-right">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((u) => (
                                    <tr key={u.id} className="border-b hover:bg-muted/50 transition-colors">
                                        <td className="px-4 py-3 flex items-center gap-3">
                                            {u.foto ? (
                                                <img src={u.foto} alt={u.nome} className="h-8 w-8 rounded-full object-cover" />
                                            ) : (
                                                <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                                                    <User className="h-4 w-4 text-muted-foreground" />
                                                </div>
                                            )}
                                            <span className="font-medium">{u.nome}</span>
                                            {u.id === currentUser?.id && (
                                                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full ml-2">Você</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'
                                                }`}>
                                                {u.role}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${u.status === 'active' ? 'bg-green-100 text-green-700' :
                                                u.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-red-100 text-red-700'
                                                }`}>
                                                {u.status === 'active' ? 'Ativo' : u.status === 'pending' ? 'Pendente' : 'Bloqueado'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-muted-foreground">
                                            {new Date(u.data_criacao).toLocaleDateString()}
                                        </td>
                                        <td className="px-4 py-3 text-right space-x-2">
                                            {u.id !== currentUser?.id && (
                                                <>
                                                    <button
                                                        onClick={() => handleEditClick(u)}
                                                        className="inline-flex items-center justify-center h-8 w-8 rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors"
                                                        title="Editar"
                                                    >
                                                        <Edit className="h-4 w-4" />
                                                    </button>
                                                    {u.status === 'pending' && (
                                                        <button
                                                            onClick={() => handleStatusChange(u.id, 'active')}
                                                            className="inline-flex items-center justify-center h-8 w-8 rounded-md bg-green-100 text-green-700 hover:bg-green-200 transition-colors"
                                                            title="Aprovar"
                                                        >
                                                            <Check className="h-4 w-4" />
                                                        </button>
                                                    )}
                                                    {u.status === 'active' && (
                                                        <button
                                                            onClick={() => handleStatusChange(u.id, 'blocked')}
                                                            className="inline-flex items-center justify-center h-8 w-8 rounded-md bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
                                                            title="Bloquear"
                                                        >
                                                            <X className="h-4 w-4" />
                                                        </button>
                                                    )}
                                                    {u.status === 'blocked' && (
                                                        <button
                                                            onClick={() => handleStatusChange(u.id, 'active')}
                                                            className="inline-flex items-center justify-center h-8 w-8 rounded-md bg-green-100 text-green-700 hover:bg-green-200 transition-colors"
                                                            title="Desbloquear"
                                                        >
                                                            <Check className="h-4 w-4" />
                                                        </button>
                                                    )}
                                                    <button
                                                        onClick={() => handleDelete(u.id, u.nome)}
                                                        className="inline-flex items-center justify-center h-8 w-8 rounded-md bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors"
                                                        title="Excluir"
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            {/* Modal de Edição */}
            {editingUser && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full space-y-4">
                        <h3 className="text-xl font-bold">Editar Usuário</h3>

                        <div className="space-y-3">
                            <div>
                                <label className="block text-sm font-medium mb-1">Nome</label>
                                <input
                                    type="text"
                                    value={editForm.nome}
                                    onChange={(e) => setEditForm({ ...editForm, nome: e.target.value })}
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Email</label>
                                <input
                                    type="email"
                                    value={editForm.email}
                                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Role</label>
                                <select
                                    value={editForm.role}
                                    onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                                >
                                    <option value="user">user</option>
                                    <option value="admin">admin</option>
                                </select>
                            </div>
                        </div>

                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setEditingUser(null)}
                                className="px-4 py-2 border border-border rounded-md hover:bg-accent transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleEditSave}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                            >
                                Salvar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
