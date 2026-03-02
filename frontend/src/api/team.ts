/** Team management API client. */
import { client } from './client';

export interface Person {
  id: number;
  name: string;
  emp_id: string;
  email?: string;
  phone?: string;
  position?: string;
  group_id?: number;
  group?: Group;
  responsibilities_owner?: Responsibility[];
  responsibilities_backup?: Responsibility[];
  created_at: string;
}

export interface Group {
  id: number;
  name: string;
  leader_id?: number;
  leader?: Person;
  members?: Person[];
  created_at: string;
}

export interface Responsibility {
  id: number;
  name: string;
  description?: string;
  owner_id?: number;
  owner?: Person;
  backup_id?: number;
  backup?: Person;
  group_id?: number;
  group?: Group;
}

export interface CapabilityDimension {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface Capability {
  id: number;
  person_id: number;
  dimension: string;
  level: number;
  description?: string;
}

export interface WorkloadPersonResponse {
  person_id: number;
  person_name: string;
  workload: number;
  task_count: number;
  tasks: { id: number; name: string }[];
}

export interface WorkloadGroupResponse {
  group_id: number;
  group_name: string;
  workload: number;
  member_count: number;
  member_workloads: WorkloadPersonResponse[];
}

export interface WorkloadMonthlySummary {
  total_workload: number;
  avg_workload: number;
  highest_load: string | null;
  highest_load_value: number | null;
  person_workloads: Array<{
    person_id: number;
    person_name: string;
    workload: number;
    task_count: number;
  }>;
}

export interface APIResponse<T> {
  code: number;
  message: string;
  data: T | null;
}

// Person APIs
export const personApi = {
  getPersons: async (params?: { skip?: number; limit?: number; search?: string }) => {
    const response = await client.get<APIResponse<Person[]>>('/team/persons', { params });
    return response.data.data || [];
  },

  getPerson: async (id: number) => {
    const response = await client.get<APIResponse<Person>>(`/team/persons/${id}`);
    return response.data.data;
  },

  createPerson: async (data: {
    name: string;
    emp_id: string;
    email?: string;
    phone?: string;
    position?: string;
    group_id?: number;
  }) => {
    const response = await client.post<APIResponse<Person>>('/team/persons', data);
    return response.data.data;
  },

  updatePerson: async (id: number, data: Partial<Person>) => {
    const response = await client.put<APIResponse<Person>>(`/team/persons/${id}`, data);
    return response.data.data;
  },

  deletePerson: async (id: number) => {
    await client.delete<APIResponse<null>>(`/team/persons/${id}`);
  },

  getPersonCapabilities: async (id: number) => {
    const response = await client.get<APIResponse<Capability[]>>(`/team/persons/${id}/capabilities`);
    return response.data.data || [];
  },

  updatePersonCapabilities: async (id: number, capabilities: Array<{
    dimension: string;
    level: number;
    description?: string;
  }>) => {
    const response = await client.put<APIResponse<Capability[]>>(`/team/persons/${id}/capabilities`, capabilities);
    return response.data.data || [];
  },
};

export interface AchievementExport {
  task_id: number;
  task_name: string;
  emp_id: string;
  name: string;
  plan_start: string;
  plan_end: string;
  actual_end: string;
  completion_status: string;
  early: number;
  on_time: number;
  slightly_late: number;
  severely_late: number;
}

export const achievementExportApi = {
  exportAchievementExcel: async (params?: {
    version_ids?: string;
    iteration_ids?: string;
    person_ids?: string;
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await client.get('/team/achievement/export', {
      params,
      responseType: 'blob'
    });
    return response;
  },
};

// Group APIs
export const groupApi = {
  getGroups: async (params?: { skip?: number; limit?: number }) => {
    const response = await client.get<APIResponse<Group[]>>('/team/groups', { params });
    return response.data.data || [];
  },

  getGroup: async (id: number) => {
    const response = await client.get<APIResponse<Group>>(`/team/groups/${id}`);
    return response.data.data;
  },

  createGroup: async (data: {
    name: string;
    leader_id?: number;
    description?: string;
  }) => {
    const response = await client.post<APIResponse<Group>>('/team/groups', data);
    return response.data.data;
  },

  updateGroup: async (id: number, data: Partial<Group>) => {
    const response = await client.put<APIResponse<Group>>(`/team/groups/${id}`, data);
    return response.data.data;
  },

  deleteGroup: async (id: number) => {
    await client.delete<APIResponse<null>>(`/team/groups/${id}`);
  },
};

// Responsibility APIs
export const responsibilityApi = {
  getResponsibilities: async (params?: { group_id?: number; skip?: number; limit?: number }) => {
    const response = await client.get<APIResponse<Responsibility[]>>('/team/responsibilities', { params });
    return response.data.data || [];
  },

  createResponsibility: async (data: {
    name: string;
    description?: string;
    owner_id?: number;
    backup_id?: number;
    group_id?: number;
  }) => {
    const response = await client.post<APIResponse<Responsibility>>('/team/responsibilities', data);
    return response.data.data;
  },

  updateResponsibility: async (id: number, data: Partial<Responsibility>) => {
    const response = await client.put<APIResponse<Responsibility>>(`/team/responsibilities/${id}`, data);
    return response.data.data;
  },

  deleteResponsibility: async (id: number) => {
    await client.delete<APIResponse<null>>(`/team/responsibilities/${id}`);
  },
};

// Capability Dimension APIs
export const capabilityApi = {
  getDimensions: async () => {
    const response = await client.get<APIResponse<CapabilityDimension[]>>('/team/capability-dimensions');
    return response.data.data || [];
  },

  createDimension: async (data: {
    name: string;
    description?: string;
    is_active?: boolean;
  }) => {
    const response = await client.post<APIResponse<CapabilityDimension>>('/team/capability-dimensions', data);
    return response.data.data;
  },

  updateDimension: async (id: number, data: Partial<CapabilityDimension>) => {
    const response = await client.put<APIResponse<CapabilityDimension>>(`/team/capability-dimensions/${id}`, data);
    return response.data.data;
  },

  deleteDimension: async (id: number) => {
    await client.delete<APIResponse<null>>(`/team/capability-dimensions/${id}`);
  },
};

// Workload APIs
export const workloadApi = {
  getPersonWorkload: async (personId: number, startDate: string, endDate: string) => {
    const response = await client.get<APIResponse<WorkloadPersonResponse>>(
      `/team/workload/person/${personId}`,
      { params: { start_date: startDate, end_date: endDate } }
    );
    return response.data.data;
  },

  getGroupWorkload: async (groupId: number, startDate: string, endDate: string) => {
    const response = await client.get<APIResponse<WorkloadGroupResponse>>(
      `/team/workload/group/${groupId}`,
      { params: { start_date: startDate, end_date: endDate } }
    );
    return response.data.data;
  },

  getMonthlyWorkloadSummary: async (month: number, year: number) => {
    const response = await client.get<APIResponse<WorkloadMonthlySummary>>(
      '/team/workload/monthly-summary',
      { params: { month, year } }
    );
    return response.data.data;
  },
};

export interface KeyFigure {
  id: number;
  group_id: number;
  type: string;
  person_id: number;
  person_name?: string;
}

// Key Figures APIs
export const keyFigureApi = {
  getGroupKeyFigures: async (groupId: number) => {
    const response = await client.get<APIResponse<KeyFigure[]>>(
      `/team/groups/${groupId}/key-figures`
    );
    return response.data.data || [];
  },

  createKeyFigure: async (groupId: number, data: {
    type: string;
    person_id: number;
  }) => {
    const response = await client.post<APIResponse<{ id: number; type: string }>>(
      `/team/groups/${groupId}/key-figures`,
      data
    );
    return response.data.data;
  },

  deleteKeyFigure: async (groupId: number, kfId: number) => {
    await client.delete<APIResponse<null>>(
      `/team/groups/${groupId}/key-figures/${kfId}`
    );
  },
};

export interface TeamStructureGraph {
  nodes: Array<{
    id: string;
    name: string;
    type: 'group' | 'person' | 'responsibility';
    [key: string]: any;
  }>;
  edges: Array<{
    source: string;
    target: string;
    type: string;
    label?: string;
  }>;
}

export interface CapabilityRadarData {
  person_id?: number;
  person_name?: string;
  group_id?: number;
  group_name?: string;
  member_count?: number;
  dimensions: string[];
  values: number[];
}

// Team Structure Graph APIs
export const graphApi = {
  getTeamStructureGraph: async () => {
    const response = await client.get<APIResponse<TeamStructureGraph>>('/team/graph/team-structure');
    return response.data.data || { nodes: [], edges: [] };
  },
};

// Capability Radar APIs
export const radarApi = {
  getPersonCapabilityRadar: async (personId: number) => {
    const response = await client.get<APIResponse<CapabilityRadarData>>(
      `/team/radar/capability/person/${personId}`
    );
    return response.data.data || { dimensions: [], values: [] };
  },

  getGroupCapabilityRadar: async (groupId: number) => {
    const response = await client.get<APIResponse<CapabilityRadarData>>(
      `/team/radar/capability/group/${groupId}`
    );
    return response.data.data || { dimensions: [], values: [] };
  },
};
