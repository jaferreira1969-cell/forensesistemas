import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Tooltip } from 'react-leaflet';
import { getOperacoes, getMapData, Operacao } from '@/services/api';
import { getDefaultOperationId } from '@/utils/defaultOperation';
import { Card, CardContent } from '@/components/ui/card';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { HeaderPortal } from '@/components/HeaderPortal';

// Fix Leaflet default icon issue with webpack/vite
delete (L.Icon.Default.prototype as any)._getIconUrl;

L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

export default function MapView() {
    const [operacoes, setOperacoes] = useState<Operacao[]>([]);
    const [selectedOp, setSelectedOp] = useState<string>('');
    const [markers, setMarkers] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [dataInicio, setDataInicio] = useState('');
    const [dataFim, setDataFim] = useState('');

    useEffect(() => {
        loadOperacoes();
    }, []);

    useEffect(() => {
        if (selectedOp) {
            loadMapData();
        }
    }, [selectedOp]);

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

    const loadMapData = async () => {
        setLoading(true);
        try {
            const data = await getMapData(
                Number(selectedOp),
                dataInicio || undefined,
                dataFim || undefined
            );
            console.log('Map data received:', data);
            console.log('Number of markers:', data.length);
            if (data.length > 0) {
                console.log('First marker:', data[0]);
            }
            setMarkers(data);
        } catch (error) {
            console.error("Erro ao carregar mapa", error);
        } finally {
            setLoading(false);
        }
    };

    const handleFilter = () => {
        loadMapData();
    };

    const handleClearFilters = () => {
        setDataInicio('');
        setDataFim('');
        // Reload without filters
        setTimeout(() => loadMapData(), 100);
    };

    return (
        <div className="p-6 space-y-6 h-full flex flex-col">
            <HeaderPortal>
                <div className="flex justify-between items-center w-full">
                    <h2 className="text-xl font-bold tracking-tight">Geolocalização de IPs</h2>
                    <div className="flex gap-3 items-center">
                        <select
                            className="p-1.5 border rounded bg-background text-sm min-w-[150px]"
                            value={selectedOp}
                            onChange={(e) => setSelectedOp(e.target.value)}
                        >
                            {operacoes.map(op => (
                                <option key={op.id} value={op.id}>{op.nome}</option>
                            ))}
                        </select>
                        <div className="flex items-center gap-2">
                            <label className="text-sm font-medium whitespace-nowrap">Data Início:</label>
                            <input
                                type="date"
                                className="p-1.5 border rounded bg-background text-sm"
                                value={dataInicio}
                                onChange={(e) => setDataInicio(e.target.value)}
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <label className="text-sm font-medium whitespace-nowrap">Data Fim:</label>
                            <input
                                type="date"
                                className="p-1.5 border rounded bg-background text-sm"
                                value={dataFim}
                                onChange={(e) => setDataFim(e.target.value)}
                            />
                        </div>
                        <button
                            className="bg-primary text-primary-foreground hover:bg-primary/90 px-3 py-1.5 rounded transition-colors text-sm"
                            onClick={handleFilter}
                        >
                            Filtrar
                        </button>
                        <button
                            className="bg-secondary text-secondary-foreground hover:bg-secondary/80 px-3 py-1.5 rounded transition-colors text-sm"
                            onClick={handleClearFilters}
                        >
                            Limpar
                        </button>
                    </div>
                </div>
            </HeaderPortal>

            <Card className="flex-1 flex flex-col overflow-hidden">
                <CardContent className="p-0 flex-1 relative">
                    {loading && (
                        <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-[1000]">
                            <span>Carregando...</span>
                        </div>
                    )}
                    <MapContainer center={[-15.7801, -47.9292]} zoom={4} style={{ height: '100%', width: '100%' }}>
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        />
                        {markers.map(m => (
                            <Marker key={m.id} position={[m.latitude, m.longitude]}>
                                <Tooltip direction="top" offset={[0, -20]} opacity={1}>
                                    <div className="text-xs font-mono">
                                        {m.telefones && m.telefones.map((t: string) => (
                                            <div key={t}>{t}</div>
                                        ))}
                                    </div>
                                </Tooltip>
                                <Popup>
                                    <div className="space-y-2 min-w-[200px]">
                                        <div className="border-b pb-1">
                                            <div className="font-bold text-lg">{m.endereco}</div>
                                            <div className="text-sm text-muted-foreground">{m.cidade}, {m.pais}</div>
                                            {m.provedor && <div className="text-xs text-muted-foreground">{m.provedor}</div>}
                                        </div>

                                        {m.telefones && m.telefones.length > 0 && (
                                            <div>
                                                <strong className="text-xs uppercase text-muted-foreground">Usuários do IP:</strong>
                                                <ul className="text-sm font-mono mt-1">
                                                    {m.telefones.map((tel: string, idx: number) => (
                                                        <li key={idx} className="flex items-center gap-1">
                                                            <span className="w-2 h-2 rounded-full bg-green-500"></span>
                                                            {tel}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        {m.conexoes && m.conexoes.length > 0 && (
                                            <div className="pt-2 border-t">
                                                <strong className="text-xs uppercase text-muted-foreground">Ligações (Origem &rarr; Destino):</strong>
                                                <ul className="text-xs mt-1 space-y-1 max-h-[150px] overflow-y-auto">
                                                    {m.conexoes.map((conn: string, idx: number) => (
                                                        <li key={idx} className="font-mono bg-muted p-1 rounded">
                                                            {conn}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </Popup>
                            </Marker>
                        ))}
                    </MapContainer>
                </CardContent>
            </Card>

            <div className="text-sm text-muted-foreground">
                {markers.length} IPs geolocalizados
                {(dataInicio || dataFim) && ' (filtrados)'}
            </div>
        </div>
    );
}
