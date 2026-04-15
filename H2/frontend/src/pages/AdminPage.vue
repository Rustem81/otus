<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <q-icon name="admin_panel_settings" size="md" class="q-mr-sm text-primary" />
      <div class="text-h6">Панель администратора</div>
    </div>

    <div class="row q-col-gutter-md">
      <!-- System Health -->
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1 q-mb-md">Состояние системы</div>
            <div class="row q-col-gutter-md">
              <div v-for="dep in healthDeps" :key="dep.name" class="col-12 col-sm-4">
                <q-card flat :class="dep.status === 'ok' ? 'bg-green-1' : dep.status === 'degraded' ? 'bg-orange-1' : 'bg-red-1'">
                  <q-card-section class="q-pa-sm">
                    <div class="row items-center">
                      <q-icon
                        :name="dep.status === 'ok' ? 'check_circle' : dep.status === 'degraded' ? 'warning' : 'error'"
                        :color="dep.status === 'ok' ? 'positive' : dep.status === 'degraded' ? 'warning' : 'negative'"
                        size="sm"
                        class="q-mr-sm"
                      />
                      <div>
                        <div class="text-weight-medium">{{ dep.label }}</div>
                        <div class="text-caption">{{ dep.status.toUpperCase() }}</div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Source Management -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1">Источники данных</div>
          </q-card-section>
          <q-list separator>
            <q-item v-for="source in sources" :key="source.id">
              <q-item-section avatar>
                <q-icon :name="source.type === 'pair' ? 'currency_exchange' : 'cloud'" :color="source.enabled ? 'primary' : 'grey'" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ source.name }}</q-item-label>
                <q-item-label caption>
                  <q-badge :color="getStatusColor(source.status)" :label="source.status.toUpperCase()" class="q-mr-xs" />
                  {{ source.type === 'pair' ? 'Валютная пара' : 'API источник' }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-toggle v-model="source.enabled" @update:model-value="toggleSource(source)" />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <!-- Error Stats -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1">Ошибки за 24 часа</div>
          </q-card-section>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <q-icon
                :name="errorStats.total === 0 ? 'check_circle' : 'error_outline'"
                :color="errorStats.total === 0 ? 'positive' : 'warning'"
                size="lg"
                class="q-mr-md"
              />
              <div>
                <div class="text-h4">{{ errorStats.total }}</div>
                <div class="text-caption text-grey">всего ошибок</div>
              </div>
            </div>
            <q-list v-if="Object.keys(errorStats.by_type).length" dense bordered separator class="rounded-borders">
              <q-item v-for="(count, type) in errorStats.by_type" :key="type">
                <q-item-section>
                  <q-item-label>{{ type }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-badge color="warning" :label="String(count)" />
                </q-item-section>
              </q-item>
            </q-list>
            <div v-else class="text-caption text-grey text-center q-pa-md">
              Ошибок не обнаружено
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';

const $q = useQuasar();

interface HealthDep { name: string; label: string; status: string }
interface Source { id: string; name: string; type: string; status: string; enabled: boolean }
interface ErrorStats { total: number; by_type: Record<string, number> }

const healthDeps = ref<HealthDep[]>([
  { name: 'postgres', label: 'PostgreSQL', status: 'ok' },
  { name: 'redis', label: 'Redis', status: 'ok' },
  { name: 'p2p_source', label: 'P2P источник', status: 'ok' },
]);

const sources = ref<Source[]>([
  { id: '1', name: 'RUB / USDT', type: 'pair', status: 'ok', enabled: true },
  { id: '2', name: 'Mock Server (p2p.army)', type: 'source', status: 'ok', enabled: true },
]);

const errorStats = ref<ErrorStats>({ total: 0, by_type: {} });

function getStatusColor(status: string): string {
  return status === 'ok' ? 'positive' : status === 'degraded' ? 'warning' : 'negative';
}

async function toggleSource(source: Source) {
  $q.notify({
    type: 'info',
    message: `${source.name}: ${source.enabled ? 'включён' : 'выключен'}`,
  });
}

onMounted(async () => {
  try {
    const resp = await api.get('/health');
    if (resp.data?.dependencies) {
      for (const dep of healthDeps.value) {
        dep.status = resp.data.dependencies[dep.name] || 'ok';
      }
    }
  } catch { /* defaults */ }
});
</script>
