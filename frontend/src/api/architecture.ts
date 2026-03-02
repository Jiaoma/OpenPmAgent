/** Architecture management API client. */
import { client } from './client';

export interface Module {
  id: number;
  name: string;
  parent_id?: number;
  children?: Module[];
  functions?: FunctionModule[];
  created_at: string;
}

export interface Function {
  id: number;
  name: string;
  parent_id?: number;
  responsibility_id?: number;
  responsibility?: Responsibility;
  functions?: FunctionModule[];
  source_flows?: DataFlow[];
  target_flows?: DataFlow[];
  created_at: string;
}

export interface Responsibility {
  id: number;
  name: string;
  description?: string;
}

export interface FunctionModule {
  id: number;
  function_id: number;
  function_name?: string;
  module_id: number;
  module_name?: string;
  order: number;
}

export interface DataFlow {
  id: number;
  source_function_id: number;
  source_function_name?: string;
  target_function_id: number;
  target_function_name?: string;
  order: number;
  description?: string;
}

export interface APIResponse<T> {
  code: number;
  message: string;
  data: T | null;
}

// Module APIs
export const moduleApi = {
  getModules: async () => {
    const response = await client.get<APIResponse<Module[]>>('/architecture/modules');
    return response.data.data || [];
  },

  getModule: async (id: number) => {
    const response = await client.get<APIResponse<Module>>(`/architecture/modules/${id}`);
    return response.data.data;
  },

  createModule: async (data: { name: string; parent_id?: number }) => {
    const response = await client.post<APIResponse<Module>>('/architecture/modules', data);
    return response.data.data;
  },

  updateModule: async (id: number, data: Partial<Module>) => {
    const response = await client.put<APIResponse<Module>>(`/architecture/modules/${id}`, data);
    return response.data.data;
  },

  deleteModule: async (id: number) => {
    await client.delete<APIResponse<null>>(`/architecture/modules/${id}`);
  },

  moveModule: async (id: number, parent_id: number) => {
    const response = await client.post<APIResponse<Module>>(`/architecture/modules/${id}/move`, { parent_id });
    return response.data.data;
  },

  exportModulesMermaid: async () => {
    const response = await client.get<APIResponse<{ mermaid: string }>>('/architecture/modules/mermaid');
    return response.data.data?.mermaid;
  },
};

// Function APIs
export const functionApi = {
  getFunctions: async (responsibility_id?: number) => {
    const params = responsibility_id ? { responsibility_id } : {};
    const response = await client.get<APIResponse<Function[]>>('/architecture/functions', { params });
    return response.data.data || [];
  },

  getFunction: async (id: number) => {
    const response = await client.get<APIResponse<Function>>(`/architecture/functions/${id}`);
    return response.data.data;
  },

  createFunction: async (data: {
    name: string;
    parent_id?: number;
    responsibility_id?: number;
  }) => {
    const response = await client.post<APIResponse<Function>>('/architecture/functions', data);
    return response.data.data;
  },

  updateFunction: async (id: number, data: Partial<Function>) => {
    const response = await client.put<APIResponse<Function>>(`/architecture/functions/${id}`, data);
    return response.data.data;
  },

  deleteFunction: async (id: number) => {
    await client.delete<APIResponse<null>>(`/architecture/functions/${id}`);
  },

  moveFunction: async (id: number, parent_id: number) => {
    const response = await client.post<APIResponse<Function>>(`/architecture/functions/${id}/move`, { parent_id });
    return response.data.data;
  },

  getFunctionModules: async (functionId: number) => {
    const response = await client.get<APIResponse<FunctionModule[]>>(`/architecture/functions/${functionId}/modules`);
    return response.data.data || [];
  },

  updateFunctionModules: async (functionId: number, modules: Array<{
    function_id: number;
    module_id: number;
    order: number;
  }>) => {
    const response = await client.post<APIResponse<FunctionModule[]>>(`/architecture/functions/${functionId}/modules`, modules);
    return response.data.data || [];
  },

  getFunctionDataFlows: async (functionId: number) => {
    const response = await client.get<APIResponse<DataFlow[]>>(`/architecture/functions/${functionId}/data-flows`);
    return response.data.data || [];
  },

  updateFunctionDataFlows: async (functionId: number, flows: Array<{
    source_function_id: number;
    target_function_id: number;
    order: number;
    description?: string;
  }>) => {
    const response = await client.post<APIResponse<DataFlow[]>>(`/architecture/functions/${functionId}/data-flows`, flows);
    return response.data.data || [];
  },

  exportFunctionsMermaid: async () => {
    const response = await client.get<APIResponse<{ mermaid: string }>>('/architecture/functions/mermaid');
    return response.data.data?.mermaid;
  },
};

// Responsibility-Function Relation APIs
export const relationApi = {
  getResponsibilityFunctionRelations: async () => {
    const response = await client.get<APIResponse<Array<{
      id: number;
      responsibility_id: number;
      function_id: number;
      function_name: string;
      responsibility_name: string;
    }>>>('/architecture/relations/responsibility-functions');
    return response.data.data || [];
  },

  createResponsibilityFunctionRelation: async (data: {
    responsibility_id: number;
    function_id: number;
  }) => {
    const response = await client.post<APIResponse<{ id: number; name: string }>>('/architecture/relations/responsibility-functions', data);
    return response.data.data;
  },

  deleteResponsibilityFunctionRelation: async (id: number) => {
    await client.delete<APIResponse<null>>(`/architecture/relations/responsibility-functions/${id}`);
  },
};
