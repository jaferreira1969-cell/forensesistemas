import { useState } from 'react';
import { Filter, X } from 'lucide-react';

export interface FilterState {
    dataInicio?: string;
    dataFim?: string;
    tipo?: string;
    telefone?: string;
    dispositivo?: string;
}

interface FilterPanelProps {
    filters: FilterState;
    onFilterChange: (filters: FilterState) => void;
    types?: string[];
}

export function FilterPanel({ filters, onFilterChange, types = [] }: FilterPanelProps) {
    const [isOpen, setIsOpen] = useState(false);

    const handleChange = (key: keyof FilterState, value: string) => {
        onFilterChange({ ...filters, [key]: value || undefined });
    };

    const clearFilters = () => {
        onFilterChange({});
    };

    const hasActiveFilters = Object.values(filters).some(v => v);

    return (
        <div className="border border-border rounded-lg p-4 bg-card">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Filter className="w-5 h-5" />
                    <h3 className="font-semibold">Filtros Avançados</h3>
                    {hasActiveFilters && (
                        <span className="px-2 py-1 text-xs bg-primary text-primary-foreground rounded">
                            Ativos
                        </span>
                    )}
                </div>
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="text-sm text-muted-foreground hover:text-foreground"
                >
                    {isOpen ? 'Ocultar' : 'Mostrar'}
                </button>
            </div>

            {isOpen && (
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Data Início</label>
                            <input
                                type="date"
                                value={filters.dataInicio || ''}
                                onChange={(e) => handleChange('dataInicio', e.target.value)}
                                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Data Fim</label>
                            <input
                                type="date"
                                value={filters.dataFim || ''}
                                onChange={(e) => handleChange('dataFim', e.target.value)}
                                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {types.length > 0 && (
                            <div>
                                <label className="block text-sm font-medium mb-1">Tipo de Mensagem</label>
                                <select
                                    value={filters.tipo || ''}
                                    onChange={(e) => handleChange('tipo', e.target.value)}
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                                >
                                    <option value="">Todos</option>
                                    {types.map(type => (
                                        <option key={type} value={type}>{type}</option>
                                    ))}
                                </select>
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium mb-1">Telefone</label>
                            <input
                                type="text"
                                placeholder="Ex: 5562..."
                                value={filters.telefone || ''}
                                onChange={(e) => handleChange('telefone', e.target.value)}
                                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">Dispositivo</label>
                            <input
                                type="text"
                                placeholder="Ex: android, iphone..."
                                value={filters.dispositivo || ''}
                                onChange={(e) => handleChange('dispositivo', e.target.value)}
                                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                            />
                        </div>
                    </div>

                    {hasActiveFilters && (
                        <button
                            onClick={clearFilters}
                            className="flex items-center gap-2 px-4 py-2 text-sm bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90 transition-colors"
                        >
                            <X className="w-4 h-4" />
                            Limpar Filtros
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
