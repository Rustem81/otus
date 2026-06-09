const COUNTER_ID = import.meta.env.VITE_YM_COUNTER_ID;

/**
 * Инициализация Яндекс.Метрики.
 * No-op если VITE_YM_COUNTER_ID не задан или не production.
 * Приложение работает без аналитики — тесты не падают.
 */
export function initMetrika(): void {
  if (!import.meta.env.PROD || !COUNTER_ID) return;

  // Динамическая загрузка tag.js
  const script = document.createElement("script");
  script.src = "https://mc.yandex.ru/metrika/tag.js";
  script.async = true;
  script.onload = () => {
    window.ym?.(Number(COUNTER_ID), "init", {
      clickmap: true,
      trackLinks: true,
      accurateTrackBounce: true,
      webvisor: true,
    });
  };
  document.head.appendChild(script);
}

/**
 * Отправка pageview при смене роута (SPA).
 */
export function trackPageView(url: string): void {
  if (!import.meta.env.PROD || !COUNTER_ID) return;
  window.ym?.(Number(COUNTER_ID), "hit", url);
}

/**
 * Отправка целевого события (reachGoal).
 */
export function trackEvent(goal: string, params?: Record<string, unknown>): void {
  if (!import.meta.env.PROD || !COUNTER_ID) return;
  window.ym?.(Number(COUNTER_ID), "reachGoal", goal, params);
}
