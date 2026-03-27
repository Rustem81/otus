// TypeScript declarations for Quasar
declare module 'quasar/wrappers' {
  import { Plugin } from 'vue';

  interface BootFileParams {
    app: import('vue').App;
    router: import('vue-router').Router;
    store?: unknown;
    redirect: (url: string) => void;
    urlPath: string;
    publicPath: string;
  }

  export function boot(callback: (params: BootFileParams) => void): Plugin;
}

declare module 'quasar' {
  export * from 'quasar';
}
