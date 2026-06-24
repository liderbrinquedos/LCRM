import { create } from 'zustand';
import { opportunitiesApi, type Opportunity, type DashboardKPIs, type DashboardStats } from '@/services/api';

interface OpportunityState {
  opportunities: Opportunity[];
  kpis: DashboardKPIs | null;
  stats: DashboardStats | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchOpportunities: (params?: any) => Promise<void>;
  fetchKPIs: () => Promise<void>;
  fetchStats: () => Promise<void>;
  updateOpportunity: (id: number, data: Partial<Opportunity>) => Promise<void>;
  setSelectedOpportunity: (opp: Opportunity | null) => void;
  selectedOpportunity: Opportunity | null;
}

export const useOpportunityStore = create<OpportunityState>((set, get) => ({
  opportunities: [],
  kpis: null,
  stats: null,
  loading: false,
  error: null,
  selectedOpportunity: null,

  fetchOpportunities: async (params) => {
    set({ loading: true, error: null });
    try {
      const data = await opportunitiesApi.getAll(params);
      set({ opportunities: data, loading: false });
    } catch (error) {
      set({ error: 'Erro ao carregar oportunidades', loading: false });
    }
  },

  fetchKPIs: async () => {
    try {
      const data = await opportunitiesApi.getKPIs();
      set({ kpis: data });
    } catch (error) {
      console.error('Erro ao carregar KPIs');
    }
  },

  fetchStats: async () => {
    try {
      const data = await opportunitiesApi.getStats();
      set({ stats: data });
    } catch (error) {
      console.error('Erro ao carregar estatísticas');
    }
  },

  updateOpportunity: async (id, data) => {
    try {
      await opportunitiesApi.update(id, data);
      await get().fetchOpportunities();
    } catch (error) {
      set({ error: 'Erro ao atualizar oportunidade' });
    }
  },

  setSelectedOpportunity: (opp) => set({ selectedOpportunity: opp }),
}));
