import { usageSeries } from '../data/mock';
import type { UsagePoint } from '../types/domain';

const PREFIX = 'healthintel.portal.';

export type AuditStatus = 'sucesso' | 'erro' | 'aviso' | 'info';

export interface AuditEvent {
  id: string;
  timestamp: string;
  tipo: string;
  usuario: string;
  detalhe: string;
  status: AuditStatus;
}

export interface LeadRecord {
  id: string;
  timestamp: string;
  nome: string;
  email: string;
  empresa: string;
  perfil: string;
  plano?: string;
  origem?: string;
  mensagem: string;
}

export interface UpgradeRequest {
  id: string;
  timestamp: string;
  plano: string;
  justificativa: string;
  status: 'registrada';
}

export interface TeamInvite {
  id: string;
  timestamp: string;
  email: string;
  papel: 'Owner' | 'Admin' | 'Leitor' | 'Billing';
  status: 'pendente' | 'cancelado' | 'removido';
}

export interface SecuritySettings {
  domains: string;
  ips: string;
  twoFactorStatus: 'desativado' | 'pendente';
}

function key(name: string): string {
  return `${PREFIX}${name}`;
}

function safeRead<T>(name: string, fallback: T): T {
  const raw = localStorage.getItem(key(name));
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function write<T>(name: string, value: T): void {
  localStorage.setItem(key(name), JSON.stringify(value));
}

export function createId(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function addAuditEvent(event: Omit<AuditEvent, 'id' | 'timestamp'>): AuditEvent {
  const next: AuditEvent = {
    id: createId('audit'),
    timestamp: new Date().toISOString(),
    ...event
  };
  const events = safeRead<AuditEvent[]>('audit', []);
  write('audit', [next, ...events].slice(0, 100));
  return next;
}

export function getAuditEvents(): AuditEvent[] {
  return safeRead<AuditEvent[]>('audit', []);
}

export function addLead(lead: Omit<LeadRecord, 'id' | 'timestamp'>): LeadRecord {
  const next: LeadRecord = { id: createId('lead'), timestamp: new Date().toISOString(), ...lead };
  write('leads', [next, ...safeRead<LeadRecord[]>('leads', [])]);
  return next;
}

export function addUpgradeRequest(request: Omit<UpgradeRequest, 'id' | 'timestamp' | 'status'>): UpgradeRequest {
  const next: UpgradeRequest = {
    id: createId('upgrade'),
    timestamp: new Date().toISOString(),
    status: 'registrada',
    ...request
  };
  write('upgrade_requests', [next, ...safeRead<UpgradeRequest[]>('upgrade_requests', [])]);
  return next;
}

export function getUpgradeRequests(): UpgradeRequest[] {
  return safeRead<UpgradeRequest[]>('upgrade_requests', []);
}

export function addTeamInvite(invite: Omit<TeamInvite, 'id' | 'timestamp' | 'status'>): TeamInvite {
  const next: TeamInvite = {
    id: createId('invite'),
    timestamp: new Date().toISOString(),
    status: 'pendente',
    ...invite
  };
  write('team_invites', [next, ...safeRead<TeamInvite[]>('team_invites', [])]);
  return next;
}

export function getTeamInvites(): TeamInvite[] {
  return safeRead<TeamInvite[]>('team_invites', []);
}

export function updateTeamInvites(invites: TeamInvite[]): void {
  write('team_invites', invites);
}

export function getSecuritySettings(): SecuritySettings {
  return safeRead<SecuritySettings>('security', {
    domains: '',
    ips: '',
    twoFactorStatus: 'desativado'
  });
}

export function saveSecuritySettings(settings: SecuritySettings): void {
  write('security', settings);
}

export function getUsageData(): UsagePoint[] {
  return safeRead<UsagePoint[]>('usage_demo', usageSeries);
}

export function savePortalPreference<T>(name: string, value: T): void {
  write(`preferences.${name}`, value);
}

export function getPortalPreference<T>(name: string, fallback: T): T {
  return safeRead<T>(`preferences.${name}`, fallback);
}
