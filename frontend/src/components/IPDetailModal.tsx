import { X, Globe, MapPin, Building2 } from 'lucide-react';

interface IPDetailModalProps {
    isOpen: boolean;
    onClose: () => void;
    ipData: {
        id: string;
        endereco: string;
        provedor?: string;
        pais?: string;
        cidade?: string;
        latitude?: number;
        longitude?: number;
    };
}

export default function IPDetailModal({ isOpen, onClose, ipData }: IPDetailModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-background border border-border rounded-lg p-6 max-w-md w-full mx-4 shadow-xl" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="flex justify-between items-center mb-4">
                    <div>
                        <h3 className="text-lg font-bold">Detalhes do IP</h3>
                        <p className="text-sm text-muted-foreground">{ipData.endereco}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-accent rounded"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Informações */}
                <div className="space-y-4">
                    {/* Provedor */}
                    <div className="flex items-start gap-3">
                        <Building2 className="w-5 h-5 text-muted-foreground mt-0.5" />
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-muted-foreground">Provedor</label>
                            <p className="text-base">{ipData.provedor || 'Não identificado'}</p>
                        </div>
                    </div>

                    {/* Localização */}
                    <div className="flex items-start gap-3">
                        <MapPin className="w-5 h-5 text-muted-foreground mt-0.5" />
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-muted-foreground">Localização</label>
                            <p className="text-base">
                                {ipData.cidade && ipData.pais
                                    ? `${ipData.cidade}, ${ipData.pais}`
                                    : ipData.pais || ipData.cidade || 'Não identificada'}
                            </p>
                        </div>
                    </div>

                    {/* Coordenadas */}
                    {(ipData.latitude !== null && ipData.latitude !== undefined &&
                        ipData.longitude !== null && ipData.longitude !== undefined) && (
                            <div className="flex items-start gap-3">
                                <Globe className="w-5 h-5 text-muted-foreground mt-0.5" />
                                <div className="flex-1">
                                    <label className="block text-sm font-medium text-muted-foreground">Coordenadas</label>
                                    <p className="text-base font-mono text-sm">
                                        {ipData.latitude.toFixed(6)}, {ipData.longitude.toFixed(6)}
                                    </p>
                                </div>
                            </div>
                        )}

                    {/* Mensagem de dados incompletos */}
                    {!ipData.provedor && !ipData.pais && !ipData.cidade && (
                        <div className="mt-4 p-3 bg-muted rounded-md">
                            <p className="text-sm text-muted-foreground">
                                ℹ️ Informações de geolocalização não disponíveis para este IP
                            </p>
                        </div>
                    )}
                </div>

                {/* Botão Fechar */}
                <div className="flex mt-6">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                    >
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    );
}
