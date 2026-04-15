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
              <div v-for="(status, name) in healthDeps" :key="name" class="col-12 col-sm-4">
                <q-card flat :class="status === 'ok' ? 'bg-green-1' : status === 'degraded' ? 'bg-orange-1' : 'bg-red-1'">
                  <q-card-section class="q-pa-sm">
                    <div class="row items-center">
                      <q-icon :name="status === 'ok' ? 'check_circle' : 'error'" :color="status === 'ok' ? 'positive' : 'negative'" size="sm" class="q-mr-sm" />
                      <div>
                        <div class="text-weight-medium">{{ name }}</div>
                        <div class="text-caption">{{ String(status).toUpperCase() }}</div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Sources -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section><div class="text-subtitle1">Источники данных</div></q-card-section>
          <q-list separator>
            <q-item v-for="source in sources?.sources" :key="source.id">
              <q-item-section avatar>
                <q-icon :name="source.type === 'pair' ? 'currency_exchange' : 'cloud'" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ source.name }}</q-item-label>
                <q-item-label caption>
                  <q-badge :color="source.status === 'ok' ? 'positive' : 'negative'" :label="source.status.toUpperCase()" />
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <!-- Errors -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section><div class="text-subtitle1">Ошибки за 24ч</div></q-card-section>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <q-icon :name="(errors?.total ?? 0) === 0 ? 'check_circle' : 'error_outline'" :color="(errors?.total ?? 0) === 0 ? 'positive' : 'warning'" size="lg" class="q-mr-md" />
              <div>
                <div class="text-h4">{{ errors?.total ?? 0 }}</div>
                <div class="text-caption text-grey">всего ошибок</div>
              </div>
            </div>
            <q-list v-if="errors?.by_type && Object.keys(errors.by_type).length" dense bordered separator class="rounded-borders">
              <q-item v-for="(count, type) in errors.by_type" :key="type">
                <q-item-section>{{ type }}</q-item-section>
                <q-item-section side><q-badge color="warning" :label="String(count)" /></q-item-section>
              </q-item>
            </q-list>
            <div v-else class="text-caption text-grey text-center q-pa-md">Ошибок нет</div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useHealthHealthGet } from 'src/api/system/system';
import { useGetSourcesStatusApiV1AdminSourcesGet, useGetErrorStatsApiV1AdminErrorsGet } from 'src/api/admin/admin';

const { data: health } = useHealthHealthGet();
const { data: sources } = useGetSourcesStatusApiV1AdminSourcesGet();
const { data: errors } = useGetErrorStatsApiV1AdminErrorsGet();

const healthDeps = computed(() => {
  const h = health.value as Record<string, unknown> | undefined;
  return (h?.dependencies as Record<string, string>) ?? {};
});
</script>
