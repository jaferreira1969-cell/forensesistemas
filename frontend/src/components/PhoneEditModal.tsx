import { useState } from 'react';
import { updateTelefone } from '@/services/api';
import { X } from 'lucide-react';

interface PhoneEditModalProps {
    phone: {
        id: number;
        numero: string;
        identificacao?: string;
        categoria?: string;
        observacoes?: string;
    };
    onClose: () => void;
    onUpdate: () => void;
}

const CATEGORIAS = [
    { value: '', label: 'Sem categoria' },
    { value: 'SUSPEITO', label: '🚨 Suspeito', color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' },
    { value: 'TESTEMUNHA', label: '👁️ Testemunha', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
    { value: 'VITIMA', label: '💔 Vítima', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' },
    { value: 'OUTRO', label: '📌 Outro', color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200' },
];

export function PhoneEditModal({ phone, onClose, onUpdate }: PhoneEditModalProps) {
    const [identificacao, setIdentificacao] = useState(phone.identificacao || '');
    const [categoria, setCategoria] = useState(phone.categoria || '');
    const [observacoes, setObservacoes] = useState(phone.observacoes || '');
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        try {
            await updateTelefone(phone.id, {
                identificacao: identificacao || undefined,
                categoria: categoria || undefined,
                observacoes: observacoes || undefined,
            });
            onUpdate();
            onClose();
        } catch (error) {
            console.error('Erro ao atualizar telefone:', error);
            alert('Erro ao salvar alterações');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-background border rounded-lg shadow-lg max-w-2xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
                <div className="flex justify-between items-center p-6 border-b">
                    <div>
                        <h2 className="text-xl font-bold">Editar Telefone</h2>
                        <p className="text-sm text-muted-foreground">{phone.numero}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-muted rounded">
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Nome/Identificação</label>
                        <input
                            type="text"
                            className="w-full p-2 border rounded bg-background"
                            placeholder="Ex: João Silva"
                            value={identificacao}
                            onChange={(e) => setIdentificacao(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Categoria</label>
                        <div className="grid grid-cols-2 gap-2">
                            {CATEGORIAS.map((cat) => (
                                <button
                                    key={cat.value}
                                    onClick={() => setCategoria(cat.value)}
                                    className={`p-3 border rounded text-left transition-all ${categoria === cat.value
                                            ? 'ring-2 ring-primary ' + cat.color
                                            : 'hover:bg-muted'
                                        }`}
                                >
                                    {cat.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Observações</label>
                        <textarea
                            className="w-full p-2 border rounded bg-background resize-none"
                            rows={4}
                            placeholder="Adicione notas sobre este telefone..."
                            value={observacoes}
                            onChange={(e) => setObservacoes(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex justify-end gap-2 p-6 border-t">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 border rounded hover:bg-muted transition-colors"
                        disabled={saving}
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleSave}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
                        disabled={saving}
                    >
                        {saving ? 'Salvando...' : 'Salvar'}
                    </button>
                </div>
            </div>
        </div>
    );
}
