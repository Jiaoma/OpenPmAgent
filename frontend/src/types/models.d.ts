/** API Response Types */
export interface APIResponse<T = any> {
  code: number;
  message: string;
  data?: T;
}

export interface PaginatedData<T = any> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/** User Types */
export interface User {
  id: number;
  emp_id: string;
  is_admin: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/** Team Management Types */
export interface Person {
  id: number;
  name: string;
  emp_id: string;
  email: string;
  group_id?: number;
  role: string;
  group?: Group;
  capabilities: Capability[];
  responsibilities: Responsibility[];
}

export interface Group {
  id: number;
  name: string;
  leader_id: number;
  leader?: Person;
  members: Person[];
  responsibilities: Responsibility[];
  key_figures: KeyFigure[];
}

export interface Capability {
  id: number;
  person_id: number;
  dimension: string;
  level: number;
}

export interface CapabilityDimension {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface KeyFigure {
  id: number;
  group_id: number;
  type: string;
  person_id: number;
  person?: Person;
}

export interface Responsibility {
  id: number;
  name: string;
  group_id: number;
  owner_id: number;
  backup_id?: number;
  current_year_tasks: number[];
  group?: Group;
  owner?: Person;
  backup?: Person;
}

/** Architecture Types */
export interface Module {
  id: number;
  name: string;
  parent_id?: number;
  parent?: Module;
  children: Module[];
}

export interface Function {
  id: number;
  name: string;
  parent_id?: number;
  responsibility_id?: number;
  parent?: Function;
  children: Function[];
  responsibility?: Responsibility;
}

export interface FunctionModule {
  id: number;
  function_id: number;
  module_id: number;
  order: number;
}

export interface DataFlow {
  id: number;
  source_function_id: number;
  target_function_id: number;
  order: number;
  description?: string;
}

/** Project Management Types */
export interface Version {
  id: number;
  name: string;
  pm_name: string;
  sm_name: string;
  tm_name: string;
  iterations: Iteration[];
}

export interface Iteration {
  id: number;
  version_id: number;
  name: string;
  start_date: string;
  end_date: string;
  estimated_man_months: number;
  tasks: Task[];
}

export interface Task {
  id: number;
  iteration_id: number;
  name: string;
  start_date: string;
  end_date: string;
  man_months: number;
  status: 'pending' | 'in_progress' | 'completed';
  delivery_owner_id: number;
  developer_id: number;
  tester_id: number;
  design_doc_url?: string;
  iteration?: Iteration;
  delivery_owner?: Person;
  developer?: Person;
  tester?: Person;
  dependencies: TaskDependency[];
  relations: TaskRelation[];
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

/** Audit Types */
export interface AuditLog {
  id: number;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id: number;
  changes?: Record<string, any>;
  timestamp: string;
  status: string;
  user?: User;
}

/** Utility Types */
export interface WorkloadData {
  person_id: number;
  person_name: string;
  workload: number;
  task_count: number;
}

export interface ConflictCheck {
  has_conflicts: boolean;
  conflicts: string[];
}
