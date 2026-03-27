import { ref, readonly } from 'vue';

interface AppConfig {
  API_URL: string;
  CONFIG_SOURCE?: string;
  CONFIG_GENERATED_AT?: string;
}

// Global config from window.__appConfig (set by config.js)
declare global {
  interface Window {
    __appConfig?: AppConfig;
  }
}

const defaultConfig: AppConfig = {
  API_URL: 'http://localhost:8000',
  CONFIG_SOURCE: 'fallback',
};

function getRuntimeConfig(): AppConfig {
  if (typeof window !== 'undefined' && window.__appConfig) {
    return window.__appConfig;
  }
  return defaultConfig;
}

// Create reactive ref for config
const runtimeConfig = ref<AppConfig>(getRuntimeConfig());

export function useRuntimeConfig() {
  return {
    config: readonly(runtimeConfig),
    apiUrl: runtimeConfig.value.API_URL,
    isRuntime: runtimeConfig.value.CONFIG_SOURCE === 'runtime',
  };
}

export function getApiBaseUrl(): string {
  return getRuntimeConfig().API_URL;
}
