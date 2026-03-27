import { defineConfig } from 'orval';

export default defineConfig({
  api: {
    input: {
      target: 'http://localhost:8000/openapi.json',
    },
    output: {
      target: './src/api/client.ts',
      client: 'vue-query',
      mode: 'tags-split',
      override: {
        mutator: {
          path: './src/api/mutator.ts',
          name: 'customMutator',
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write src/api/**',
    },
  },
});
