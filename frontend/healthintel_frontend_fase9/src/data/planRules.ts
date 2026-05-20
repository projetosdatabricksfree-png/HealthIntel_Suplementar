import { getPlanBySlug } from './plans';
import type { ApiPlan, PlanSlug, PortalRole } from '../types/domain';

const LEGACY_PLAN_ALIASES: Record<string, PlanSlug> = {
  sandbox: 'starter',
  'sandbox tecnico': 'starter',
  starter_local: 'starter',
  piloto: 'pro',
  'piloto assistido': 'pro',
  core: 'pro',
  'core api': 'pro',
  essencial: 'pro',
  plus: 'max',
  'core pro': 'max',
  growth_local: 'pro',
  pro_local: 'pro',
  enterprise_local: 'enterprise',
  admin_interno: 'enterprise'
};

export type FeatureKey =
  | 'team'
  | 'security'
  | 'advancedSecurity'
  | 'usageExport'
  | 'usageWebhook'
  | 'ipAllowlist'
  | 'sso'
  | 'adminInternal';

const FEATURE_MIN_PLAN: Partial<Record<FeatureKey, PlanSlug>> = {
  team: 'pro',
  security: 'starter',
  advancedSecurity: 'pro',
  usageExport: 'pro',
  usageWebhook: 'max',
  ipAllowlist: 'pro',
  sso: 'enterprise'
};

const PLAN_ORDER: PlanSlug[] = ['free', 'starter', 'pro', 'max', 'enterprise'];

export function normalizePlanSlug(value?: string | null): PlanSlug {
  const normalized = String(value || 'free').trim().toLowerCase();
  return (LEGACY_PLAN_ALIASES[normalized] || (PLAN_ORDER.includes(normalized as PlanSlug) ? normalized : 'free')) as PlanSlug;
}

export function getCurrentPlan(value?: string | null): ApiPlan {
  return getPlanBySlug(normalizePlanSlug(value));
}

export function planRank(plan: PlanSlug): number {
  return PLAN_ORDER.indexOf(plan);
}

export function hasPlanAtLeast(value: string | undefined | null, minimum: PlanSlug): boolean {
  return planRank(normalizePlanSlug(value)) >= planRank(minimum);
}

export function canAccessFeature(planValue: string | undefined | null, feature: FeatureKey, role?: PortalRole): boolean {
  if (feature === 'adminInternal') {
    return role === 'admin_internal';
  }
  const minimum = FEATURE_MIN_PLAN[feature];
  return minimum ? hasPlanAtLeast(planValue, minimum) : false;
}

export function isInternalAdmin(role?: PortalRole): boolean {
  return role === 'admin_internal';
}
