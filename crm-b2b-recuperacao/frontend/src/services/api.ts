import axios from 'axios';

const API_BASE_URL = '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Tipos
export interface Opportunity {
  id: number;
  company_id: number;
  owner_id: number;
  motivo_perda: string;
  valor_potencial: number;
  ai_score: number;
  ai_probability: string;
  stage: string;
  priority: string;
  is_recovered: boolean;
  created_at: string;
  company?: {
    nome_fantasia: string;
    segmento: string;
  };
}

export interface DashboardKPIs {
  receita_recuperada: number;
  clientes_recuperados: number;
  clientes_em_risco: number;
  taxa_churn: number;
  taxa_reativacao: number;
  ticket_medio: number;
  ltv_medio: number;
}

export interface DashboardStats {
  total_opportunities: number;
  by_stage: Record<string, number>;
  by_priority: Record<string, number>;
  recent_interactions: number;
}

// Endpoints
export const opportunitiesApi = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    stage?: string;
    priority?: string;
    search?: string;
  }) => {
    const response = await api.get<Opportunity[]>('/opportunities/', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<Opportunity>(`/opportunities/${id}`);
    return response.data;
  },

  create: async (data: Partial<Opportunity>) => {
    const response = await api.post<Opportunity>('/opportunities/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Opportunity>) => {
    const response = await api.patch<Opportunity>(`/opportunities/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/opportunities/${id}`);
  },

  getKPIs: async () => {
    const response = await api.get<DashboardKPIs>('/opportunities/kpis');
    return response.data;
  },

  getStats: async () => {
    const response = await api.get<DashboardStats>('/opportunities/stats/dashboard');
    return response.data;
  },
};
