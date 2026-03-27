import { boot } from 'quasar/wrappers';
import { VueQueryPlugin } from '@tanstack/vue-query';

export default boot(({ app }) => {
  app.use(VueQueryPlugin, {
    queryClientConfig: {
      defaultOptions: {
        queries: {
          refetchOnWindowFocus: false,
          retry: 1,
          staleTime: 1000 * 30, // 30 seconds
        },
      },
    },
  });
});
