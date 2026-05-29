export const commercialLinks = {
  stripe: {
    starter: String(import.meta.env.VITE_STRIPE_CHECKOUT_STARTER_URL ?? '').trim(),
    pro:     String(import.meta.env.VITE_STRIPE_CHECKOUT_PRO_URL ?? '').trim(),
    max:     String(import.meta.env.VITE_STRIPE_CHECKOUT_MAX_URL ?? '').trim(),
    starterAnual: String(import.meta.env.VITE_STRIPE_CHECKOUT_STARTER_ANUAL_URL ?? '').trim(),
    proAnual:     String(import.meta.env.VITE_STRIPE_CHECKOUT_PRO_ANUAL_URL ?? '').trim(),
    maxAnual:     String(import.meta.env.VITE_STRIPE_CHECKOUT_MAX_ANUAL_URL ?? '').trim(),
  },
  contact: '/contato',
  login:   '/login',
  docs:    '/documentacao',
};
