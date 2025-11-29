import { useState, useRef, ChangeEvent } from 'react';
import { X, Upload, Trash2 } from 'lucide-react';
import { updateTelefone } from '@/services/api';
import { useToast } from '@/contexts/ToastContext';

interface NodeEditModalProps {
    isOpen: boolean;
    onClose: () => void;
    nodeData: {
        id: string;
        label: string;
        telefone_id?: number;
        identificacao?: string;
        foto?: string;
        categoria?: string;
        observacoes?: string;
    };
    operacaoId: number;
    onUpdate: () => void;
}

const CATEGORIAS = [
    { value: '', label: 'Sem categoria', emoji: '', color: '' },
    { value: 'SUSPEITO', label: 'Suspeito', emoji: '🚨', color: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-200' },
    { value: 'TESTEMUNHA', label: 'Testemunha', emoji: '👁️', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-200' },
    { value: 'VITIMA', label: 'Vítima', emoji: '💔', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark: text-purple-200' },
    { value: 'OUTRO', label: 'Outro', emoji: '📌', color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200' },
];

export default function NodeEditModal({ isOpen, onClose, nodeData, onUpdate }: NodeEditModalProps) {
    const [identificacao, setIdentificacao] = useState(nodeData.identificacao || '');
    const [foto, setFoto] = useState(nodeData.foto || '');
    const [categoria, setCategoria] = useState(nodeData.categoria || '');
    const [observacoes, setObservacoes] = useState(nodeData.observacoes || '');
    const [loading, setLoading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { addToast } = useToast();

    if (!isOpen) return null;

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            // Verificar tamanho (máximo 5MB)
            if (file.size > 5 * 1024 * 1024) {
                addToast('A imagem deve ter no máximo 5MB', 'warning');
                return;
            }

            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = reader.result as string;
                setFoto(base64);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSave = async () => {
        if (!nodeData.telefone_id) {
            addToast('Telefone não encontrado', 'error');
            return;
        }

        setLoading(true);
        try {
            await updateTelefone(nodeData.telefone_id, {
                identificacao: identificacao || undefined,
                foto: foto || undefined,
                categoria: categoria || undefined,
                observacoes: observacoes || undefined,
            });
            onUpdate();
            addToast('Alterações salvas com sucesso!', 'success');
            onClose();
        } catch (error) {
            console.error('Erro ao atualizar telefone:', error);
            addToast('Erro ao salvar alterações', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveFoto = () => {
        setFoto('');
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-background border border-border rounded-lg p-6 max-w-2xl w-full mx-4 shadow-xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="flex justify-between items-center mb-4">
                    <div>
                        <h3 className="text-lg font-bold">Editar Telefone</h3>
                        <p className="text-sm text-muted-foreground">{nodeData.id}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-accent rounded"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Nome/Identificação */}
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">
                        Nome/Identificação
                    </label>
                    <input
                        type="text"
                        value={identificacao}
                        onChange={(e) => setIdentificacao(e.target.value)}
                        placeholder="Digite um nome"
                        className="w-full px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                </div>

                {/* Categoria */}
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">
                        Categoria de Investigação
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                        {CATEGORIAS.map((cat) => (
                            <button
                                key={cat.value}
                                onClick={() => setCategoria(cat.value)}
                                className={`p-3 border rounded text-left transition-all ${categoria === cat.value
                                    ? 'ring-2 ring-primary ' + cat.color
                                    : 'hover:bg-muted border-input'
                                    }`}
                            >
                                <span className="text-lg mr-2">{cat.emoji}</span>
                                {cat.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Observações */}
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">
                        Observações/Notas
                    </label>
                    <textarea
                        value={observacoes}
                        onChange={(e) => setObservacoes(e.target.value)}
                        placeholder="Adicione notas sobre este telefone..."
                        rows={3}
                        className="w-full px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                    />
                </div>

                {/* Foto */}
                <div className="mb-6">
                    <label className="block text-sm font-medium mb-2">
                        Foto do Perfil
                    </label>

                    {foto ? (
                        <div className="space-y-2">
                            <div className="flex justify-center">
                                <img
                                    src={foto}
                                    alt="Preview"
                                    className="w-32 h-32 object-cover rounded-full border-2 border-primary"
                                />
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 border border-input rounded-md hover:bg-accent transition-colors"
                                >
                                    <Upload className="w-4 h-4" />
                                    Trocar Foto
                                </button>
                                <button
                                    onClick={handleRemoveFoto}
                                    className="px-4 py-2 border border-destructive text-destructive rounded-md hover:bg-destructive/10 transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ) : (
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-input rounded-md hover:border-primary hover:bg-accent transition-colors"
                        >
                            <Upload className="w-5 h-5" />
                            Adicionar Foto
                        </button>
                    )}

                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        className="hidden"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                        Máximo 5MB (JPG, PNG, GIF)
                    </p>
                </div>

                {/* Botões */}
                <div className="flex gap-2">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2 border border-input rounded-md hover:bg-accent transition-colors"
                        disabled={loading}
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleSave}
                        className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
                        disabled={loading}
                    >
                        {loading ? 'Salvando...' : 'Salvar'}
                    </button>
                </div>
            </div>
        </div>
    );
}
