<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">Администрирование</div>

    <div class="row q-col-gutter-md">
      <!-- Source Status -->
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-subtitle1">Статус источников</div>
          </q-card-section>

          <q-card-section>
            <q-list bordered separator>
              <q-item v-for="source in sources" :key="source.id">
                <q-item-section>
                  <q-item-label>{{ source.name }}</q-item-label>
                  <q-item-label caption>{{ source.type }}</q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-badge
                    :color="getStatusColor(source.status)"
                    :label="source.status"
                  />
                </q-item-section>

                <q-item-section side>
                  <q-toggle
                    v-model="source.enabled"
                    @update:model-value="toggleSource(source)"
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Error Stats -->
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-subtitle1">Ошибки за 24ч</div>
          </q-card-section>

          <q-card-section>
            <div class="text-h4 q-mb-md">{{ errorStats.total }}</div>

            <q-list dense>
              <q-item v-for="(count, type) in errorStats.by_type" :key="type">
                <q-item-section>{{ type }}</q-item-section>
                <q-item-section side>{{ count }}</q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Source {
  id: string;
  name: string;
  type: string;
  status: string;
  enabled: boolean;
}

interface ErrorStats {
  total: number;
  by_type: Record<string, number>;
}

const sources = ref<Source[]>([
  { id: '1', name: 'MEXC RUB/USDT', type: 'pair', status: 'ok', enabled: true },
  { id: '2', name: 'p2p.army API', type: 'source', status: 'ok', enabled: true },
]);

const errorStats = ref<ErrorStats>({
  total: 0,
  by_type: {},
});

function getStatusColor(status: string): string {
  switch (status) {
    case 'ok':
      return 'positive';
    case 'degraded':
      return 'warning';
    case 'down':
      return 'negative';
    default:
      return 'grey';
  }
}

async function toggleSource(source: Source) {
  // TODO: API call to toggle source
  console.log('Toggle source:', source.id, source.enabled);
}

async function fetchStats() {
  // TODO: API call to fetch error stats
}

onMounted(() => {
  fetchStats();
});
</script>
