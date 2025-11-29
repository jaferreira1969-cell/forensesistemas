import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
});

export interface Operacao {
    id: number;
    nome: string;
    descricao?: string;
    data_criacao: string;
}

export interface Stats {
    total_telefones: number;
    total_mensagens: number;
    total_ips: number;
}

export interface IP {
    id: number;
    endereco: string;
    pais?: string;
    cidade?: string;
    latitude?: number;
    longitude?: number;
    provedor?: string;
    telefones?: string[];
    conexoes?: string[];
}

export interface ArquivoImportado {
    id: number;
    nome: string;
    data_upload: string;
    alvo_numero?: string;
    periodo_inicio?: string;
    periodo_fim?: string;
}

export interface Mensagem {
    id: number;
    operacao_id: number;
    alvo: string;
    remetente: string;
    destinatario: string;
    ip_id?: number;
    porta?: number;
    data_hora: string;
    tipo_mensagem: string;
    ip_rel?: IP;
}

// Operações
export const getOperacoes = async () => {
    const response = await api.get<Operacao[]>('/operacoes/');
    return response.data;
};

export const createOperacao = async (nome: string) => {
    const response = await api.post<Operacao>('/operacoes/', { nome });
    return response.data;
};

export const deleteOperacao = async (operacaoId: number) => {
    const response = await api.delete(`/operacoes/${operacaoId}`);
    return response.data;
};

export const updateOperacao = async (operacaoId: number, data: { nome: string; descricao?: string }) => {
    const response = await api.put<Operacao>(`/operacoes/${operacaoId}`, data);
    return response.data;
};

// Telefones
export const getTelefoneByNumero = async (operacaoId: number, numero: string) => {
    const response = await api.get(`/telefones/by-numero/${operacaoId}/${numero}`);
    return response.data;
};

export const updateTelefone = async (telefoneId: number, data: {
    identificacao?: string;
    foto?: string;
    categoria?: string;
    observacoes?: string;
}) => {
    const response = await api.put(`/telefones/${telefoneId}`, data);
    return response.data;
};

// Dashboard
export const getStats = async (operacaoId: number) => {
    const response = await api.get<Stats>(`/dashboard/${operacaoId}/stats`);
    return response.data;
};

export const getEvolution = async (operacaoId: number) => {
    const response = await api.get<{ data: string, total: number }[]>(`/dashboard/${operacaoId}/evolution`); return response.data;
};

// Upload e Arquivos
export const getImportedFiles = async (operacaoId: number) => {
    const response = await api.get<ArquivoImportado[]>(`/upload/files/${operacaoId}`);
    return response.data;
};

export const getTopTalkers = async (operacaoId: number) => {
    const response = await api.get<any[]>(`/dashboard/${operacaoId}/telefones`);
    return response.data;
};

export const getActivityHeatmap = async (operacaoId: number) => {
    const response = await api.get<{ hour: number, day: number, count: number }[]>(`/dashboard/activity-heatmap/${operacaoId}`);
    return response.data;
};

export const getMessageTypes = async (operacaoId: number) => {
    const response = await api.get<{ tipo: string, count: number }[]>(`/dashboard/message-types/${operacaoId}`);
    return response.data;
};

export const getTopInterlocutors = async (operacaoId: number) => {
    const response = await api.get<{ numero: string, total: number }[]>(`/dashboard/top-interlocutors/${operacaoId}`);
    return response.data;
};

export const getPeakHours = async (operacaoId: number) => {
    const response = await api.get<{ hour: number, count: number }[]>(`/dashboard/peak-hours/${operacaoId}`);
    return response.data;
};

// Grafos
export const getGeneralGraph = async (operacaoId: number) => {
    const response = await api.get<any>(`/graph/${operacaoId}/general`);
    return response.data;
};

export const getCommonIpsGraph = async (operacaoId: number) => {
    const response = await api.get<any>(`/graph/${operacaoId}/common-ips`);
    return response.data;
};

export const getSharedIpsGraph = async (operacaoId: number) => {
    const response = await api.get<any>(`/graph/${operacaoId}/shared-ips`);
    return response.data;
};

// Geolocalização
export const syncGeolocation = async (operacaoId: number) => {
    const response = await api.post(`/geolocation/${operacaoId}/sync`);
    return response.data;
};

export const getMapData = async (operacaoId: number, dataInicio?: string, dataFim?: string) => {
    const params: any = {};
    if (dataInicio) params.data_inicio = dataInicio;
    if (dataFim) params.data_fim = dataFim;

    const response = await api.get<IP[]>(`/geolocation/${operacaoId}`, { params });
    return response.data;
};

// Mensagens
export const getMessages = async (
    operacaoId: number,
    skip = 0,
    limit = 50,
    search = '',
    sortBy = 'data_hora',
    order = 'desc',
    dataInicio?: string,
    dataFim?: string
) => {
    const params: any = { skip, limit, search, sort_by: sortBy, order };
    if (dataInicio) params.data_inicio = dataInicio;
    if (dataFim) params.data_fim = dataFim;

    const response = await api.get<Mensagem[]>(`/mensagens/${operacaoId}`, { params });
    return response.data;
};

// Export
export const exportPDF = async (operacaoId: number) => {
    const response = await api.get(`/export/pdf/${operacaoId}`, {
        responseType: 'blob'
    });
    return response.data;
};

export const exportExcel = async (operacaoId: number) => {
    const response = await api.get(`/export/excel/${operacaoId}`, {
        responseType: 'blob'
    });
    return response.data;
};

// Intelligence Report
export const generateIntelligenceReport = async (operacaoId: number) => {
    const response = await api.get(`/intelligence/${operacaoId}/report`, {
        responseType: 'blob'
    });
    return response.data;
};

export default api;
