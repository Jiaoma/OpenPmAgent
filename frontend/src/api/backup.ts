/** Backup management API client. */
import { apiClient } from './client';

export interface BackupCreate {
  name?: string;
  description?: string;
}

export interface BackupResponse {
  name: string;
  description: string;
  timestamp: string;
  data: {
    team?: any;
    architecture?: any;
    project?: any;
  };
}

export interface RestoreRequest {
  backup_data: any;
  restore_options?: {
    team?: boolean;
    architecture?: boolean;
    project?: boolean;
  };
}

export interface RestoreResponse {
  team: string;
  architecture: string;
  project: string;
  errors: string[];
}

export interface APIResponse<T> {
  code: number;
  message: string;
  data: T | null;
}

// Backup APIs
export const backupApi = {
  createBackup: async (data?: BackupCreate) => {
    const response = await apiClient.post<APIResponse<BackupResponse>>('/backup/create', data);
    return response.data.data;
  },

  downloadBackup: async () => {
    const response = await apiClient.get('/backup/download', {
      responseType: 'blob',
    });
    return response;
  },

  restoreFromBackup: async (data: RestoreRequest) => {
    const response = await apiClient.post<APIResponse<RestoreResponse>>('/backup/restore', data);
    return response.data.data;
  },
};
