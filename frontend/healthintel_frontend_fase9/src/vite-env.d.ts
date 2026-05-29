/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_ENABLE_DEMO_FALLBACK?: string;
  readonly VITE_APP_NAME?: string;
  readonly VITE_GOOGLE_CLIENT_ID?: string;
  readonly VITE_STRIPE_CHECKOUT_STARTER_URL?: string;
  readonly VITE_STRIPE_CHECKOUT_PRO_URL?: string;
  readonly VITE_STRIPE_CHECKOUT_MAX_URL?: string;
  readonly VITE_STRIPE_CHECKOUT_STARTER_ANUAL_URL?: string;
  readonly VITE_STRIPE_CHECKOUT_PRO_ANUAL_URL?: string;
  readonly VITE_STRIPE_CHECKOUT_MAX_ANUAL_URL?: string;
  readonly MODE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
