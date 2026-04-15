<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <q-icon name="history" size="md" class="q-mr-sm text-primary" />
      <div class="text-h6">История просмотров</div>
      <q-space />
      <q-chip icon="info" size="sm" color="grey-3">Последние 50</q-chip>
    </div>

    <div v-if="isLoading" class="column items-center q-pa-xl">
      <q-spinner-dots size="40px" color="primary" />
    </div>

    <q-card v-else-if="!history?.items?.length" flat bordered class="q-pa-xl text-center">
      <q-icon name="visibility_off" size="4em" color="grey-4" />
      <div class="text-h6 text-grey q-mt-md">Вы ещё не просматривали объявления</div>
      <div class="text-caption text-grey q-mb-md">Откройте карточку объявления — она появится здесь</div>
      <q-btn outline color="primary" label="К объявлениям" to="/" icon="arrow_back" />
    </q-card>

    <q-timeline v-else color="primary">
      <q-timeline-entry v-for="(group, date) in groupedHistory" :key="date" :subtitle="String(date)">
        <q-list bordered separator class="rounded-borders">
          <q-item v-for="entry in group" :key="entry.advertisement_id + entry.viewed_at">
            <q-item-section avatar><q-icon name="receipt_long" color="grey" /></q-item-section>
            <q-item-section>
              <q-item-label>{{ entry.advertisement_id.slice(0, 8) }}...</q-item-label>
              <q-item-label caption>{{ formatTime(entry.viewed_at) }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-timeline-entry>
    </q-timeline>
  </q-page>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useGetViewHistoryApiV1HistoryGet } from 'src/api/history/history';
import type { ViewHistoryEntry } from 'src/api/client.schemas';

const { data: history, isLoading } = useGetViewHistoryApiV1HistoryGet();

const groupedHistory = computed(() => {
  const groups: Record<string, ViewHistoryEntry[]> = {};
  for (const entry of history.value?.items ?? []) {
    const date = new Date(entry.viewed_at).toLocaleDateString('ru-RU', {
      day: 'numeric', month: 'long', year: 'numeric',
    });
    if (!groups[date]) groups[date] = [];
    groups[date].push(entry);
  }
  return groups;
});

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}
</script>
