/** Project management API client. */
import { client } from './client';

export interface Version {
  id: number;
  name: string;
  pm_name: string;
  sm_name: string;
  tm_name: string;
  iterations?: Iteration[];
  created_at: string;
}

export interface Iteration {
  id: number;
  name: string;
  version_id: number;
  version_name?: string;
  start_date: string;
  end_date: string;
  estimated_man_months: number;
  tasks?: Task[];
}

export interface Task {
  id: number;
  name: string;
  iteration_id: number;
  iteration_name?: string;
  start_date: string;
  end_date: string;
  man_months: number;
  status: 'pending' | 'in_progress' | 'completed';
  delivery_owner_id?: number;
  delivery_owner_name?: string;
  developer_id?: number;
  developer_name?: string;
  tester_id?: number;
  tester_name?: string;
  design_doc_url?: string;
  dependencies?: TaskDependency[];
  relations?: TaskRelation[];
  completion?: TaskCompletion;
}

export interface TaskDependency {
  id: number;
  task_id: number;
  depends_on_id: number;
  type: 'finish_to_start' | 'start_to_start' | 'finish_to_finish' | 'start_to_finish';
}

export interface TaskRelation {
  id: number;
  task_id: number;
  related_task_id: number;
}

export interface TaskCompletion {
  id: number;
  task_id: number;
  actual_end_date: string;
  completion_status: 'early' | 'on_time' | 'slightly_late' | 'severely_late';
}

export interface TaskAchievementStats {
  person_id: number;
  person_name: string;
  person_role: string;
  total_tasks: number;
  completed: number;
  early: number;
  on_time: number;
  slightly_late: number;
  severely_late: number;
}

export interface APIResponse<T> {
  code: number;
  message: string;
  data: T | null;
}

// Version APIs
export const versionApi = {
  getVersions: async () => {
    const response = await client.get<APIResponse<Version[]>>('/project/versions');
    return response.data.data || [];
  },

  getVersion: async (id: number) => {
    const response = await client.get<APIResponse<Version>>(`/project/versions/${id}`);
    return response.data.data;
  },

  createVersion: async (data: {
    name: string;
    pm_name: string;
    sm_name: string;
    tm_name: string;
  }) => {
    const response = await client.post<APIResponse<Version>>('/project/versions', data);
    return response.data.data;
  },

  updateVersion: async (id: number, data: Partial<Version>) => {
    const response = await client.put<APIResponse<Version>>(`/project/versions/${id}`, data);
    return response.data.data;
  },

  deleteVersion: async (id: number) => {
    await client.delete<APIResponse<null>>(`/project/versions/${id}`);
  },
};

// Iteration APIs
export const iterationApi = {
  getIterations: async (version_id?: number) => {
    const params = version_id ? { version_id } : {};
    const response = await client.get<APIResponse<Iteration[]>>('/project/iterations', { params });
    return response.data.data || [];
  },

  getIteration: async (id: number) => {
    const response = await client.get<APIResponse<Iteration>>(`/project/iterations/${id}`);
    return response.data.data;
  },

  createIteration: async (data: {
    version_id: number;
    name: string;
    start_date: string;
    end_date: string;
    estimated_man_months: number;
  }) => {
    const response = await client.post<APIResponse<Iteration>>('/project/iterations', data);
    return response.data.data;
  },

  updateIteration: async (id: number, data: Partial<Iteration>) => {
    const response = await client.put<APIResponse<Iteration>>(`/project/iterations/${id}`, data);
    return response.data.data;
  },

  deleteIteration: async (id: number) => {
    await client.delete<APIResponse<null>>(`/project/iterations/${id}`);
  },
};

// Task APIs
export const taskApi = {
  getTasks: async (params?: {
    iteration_id?: number;
    version_id?: number;
    person_id?: number;
  }) => {
    const response = await client.get<APIResponse<Task[]>>('/project/tasks', { params });
    return response.data.data || [];
  },

  getTask: async (id: number) => {
    const response = await client.get<APIResponse<Task>>(`/project/tasks/${id}`);
    return response.data.data;
  },

  createTask: async (data: {
    iteration_id: number;
    name: string;
    start_date: string;
    end_date: string;
    man_months: number;
    status?: 'pending' | 'in_progress' | 'completed';
    delivery_owner_id: number;
    developer_id: number;
    tester_id: number;
    design_doc_url?: string;
  }) => {
    const response = await client.post<APIResponse<Task>>('/project/tasks', data);
    return response.data.data;
  },

  updateTask: async (id: number, data: Partial<Task>) => {
    const response = await client.put<APIResponse<Task>>(`/project/tasks/${id}`, data);
    return response.data.data;
  },

  deleteTask: async (id: number) => {
    await client.delete<APIResponse<null>>(`/project/tasks/${id}`);
  },

  markTaskComplete: async (id: number, data: {
    actual_end_date: string;
    completion_status: 'early' | 'on_time' | 'slightly_late' | 'severely_late';
  }) => {
    const response = await client.post<APIResponse<Task>>(`/project/tasks/${id}/complete`, data);
    return response.data.data;
  },
};

export interface TaskConflict {
  task_id?: number;
  task_name?: string;
  conflicting_task_id?: number;
  conflicting_task_name?: string;
  conflict_type: string;
  person_id?: number;
}

// Task Dependencies APIs
export const taskDependencyApi = {
  addTaskDependency: async (data: {
    task_id: number;
    depends_on_id: number;
    type?: 'finish_to_start' | 'start_to_start' | 'finish_to_finish' | 'start_to_finish';
  }) => {
    const response = await client.post<APIResponse<{
      id: number;
      task_id: number;
      depends_on_id: number;
    }>>('/project/tasks/0/dependencies', data);
    return response.data.data;
  },

  deleteTaskDependency: async (taskId: number, depId: number) => {
    await client.delete<APIResponse<null>>(`/project/tasks/${taskId}/dependencies/${depId}`);
  },
};

export interface TaskRelation {
  id: number;
  task_id: number;
  related_task_id: number;
}

// Task Relations APIs
export const taskRelationApi = {
  addTaskRelation: async (data: {
    task_id: number;
    related_task_id: number;
  }) => {
    const response = await client.post<APIResponse<{
      id: number;
      task_id: number;
      related_task_id: number;
    }>>('/project/tasks/0/relations', data);
    return response.data.data;
  },

  deleteTaskRelation: async (taskId: number, relId: number) => {
    await client.delete<APIResponse<null>>(`/project/tasks/${taskId}/relations/${relId}`);
  },
};

// Task Conflict Check API
export const taskConflictApi = {
  checkTaskConflicts: async (taskId: number) => {
    const response = await client.post<APIResponse<TaskConflict[]>>(
      `/project/tasks/${taskId}/check-conflicts`,
      {}
    );
    return response.data.data || [];
  },
};

// Task Graph APIs
export const taskGraphApi = {
  getTaskGraph: async (iteration_id?: number) => {
    const params = iteration_id ? { iteration_id } : {};
    const response = await client.get<APIResponse<{
      nodes: any[];
      edges: any[];
    }>>('/project/tasks/graph', { params });
    return response.data.data || { nodes: [], edges: [] };
  },

  getLongestPath: async (iteration_id?: number) => {
    const params = iteration_id ? { iteration_id } : {};
    const response = await client.get<APIResponse<any[]>>('/project/tasks/longest-path', { params });
    return response.data.data || [];
  },

  getHighestLoadPerson: async (iteration_id?: number) => {
    const params = iteration_id ? { iteration_id } : {};
    const response = await client.get<APIResponse<any | null>>('/project/tasks/highest-load', { params });
    return response.data.data;
  },
};

// Gantt Chart APIs
export const ganttApi = {
  getGanttData: async (params?: {
    iteration_id?: number;
    version_id?: number;
  }) => {
    const response = await client.get<APIResponse<any[]>>('/project/gantt', { params });
    return response.data.data || [];
  },

  exportGanttMermaid: async (params?: {
    iteration_id?: number;
    version_id?: number;
  }) => {
    const paramsQuery = new URLSearchParams();
    if (params?.iteration_id) paramsQuery.set('iteration_id', params.iteration_id.toString());
    if (params?.version_id) paramsQuery.set('version_id', params.version_id.toString());
    const response = await client.get<APIResponse<{ mermaid: string }>>(
      `/project/gantt/mermaid?${paramsQuery.toString()}`
    );
    return response.data.data?.mermaid;
  },
};

// Achievement APIs
export const achievementApi = {
  getAchievementStats: async (params?: {
    version_ids?: string;
    iteration_ids?: string;
    person_ids?: string;
  }) => {
    const response = await client.get<APIResponse<TaskAchievementStats[]>>('/project/achievement', { params });
    return response.data.data || [];
  },
};
