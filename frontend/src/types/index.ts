export interface User {
  id: number;
  username: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Simulation {
  simulation_id: string;
  status: string;
  created_at: string;
  duration_minutes: number;
}

export interface SimulationConfig {
  BROKER_URL: string;
  BROKER_PORT: number;
  TIME_INTERVAL: number;
  TOPICS: Topic[];
  duration_minutes: number;
}

export interface Topic {
  TYPE: 'single' | 'multiple' | 'list';
  PREFIX: string;
  RANGE_START?: number;
  RANGE_END?: number;
  LIST?: string[];
  TIME_INTERVAL?: number;
  DATA: DataField[];
}

export interface DataField {
  NAME: string;
  TYPE: 'int' | 'float' | 'bool' | 'math_expression' | 'raw_values';
  MIN_VALUE?: number;
  MAX_VALUE?: number;
  MAX_STEP?: number;
  INITIAL_VALUE?: number;
  INCREASE_PROBABILITY?: number;
  RETAIN_PROBABILITY?: number;
  RESET_PROBABILITY?: number;
  RESTART_ON_BOUNDARIES?: boolean;
}
