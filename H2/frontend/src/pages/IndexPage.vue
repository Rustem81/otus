<template>
  <q-page padding>
    <!-- Header with update timer -->
    <div class="row items-center q-mb-md">
      <div class="text-h6">P2P Объявления</div>
      <q-chip
        v-if="store.lastUpdated"
        :color="updateAge > 30 ? 'warning' : 'grey-4'"
        :text-color="updateAge > 30 ? 'white' : 'dark'"
        size="sm"
        class="q-ml-md"
        icon="schedule"
      >
        Обновлено {{ updateAge }} сек назад
      </q-chip>
      <q-space />
      <q-btn-toggle
        v-model="direction"
        no-caps
        rounded
        toggle-color="primary"
        :options="[
          { label: 'Покупка', value: 'BUY' },
          { label: 'Продажа', value: 'SELL' },
        ]"
        class="q-mr-md"
        @update:model-value="store.setDirection($event)"
      />
      <q-btn flat round icon="refresh" :loading="store.isLoading" @click="store.fetchAdvertisements()">
        <q-tooltip>Обновить</q-tooltip>
      </q-btn>
    </div>

    <!-- Error Banner -->
    <q-banner v-if="store.error" class="bg-negative text-white q-mb-md" rounded>
      <template #avatar><q-icon name="error" /></template>
      {{ store.error }}
      <template #action>
        <q-btn flat label="Повторить" @click="store.fetchAdvertisements()" />
      </template>
    </q-banner>

    <!-- Quick Stats -->
    <div class="row q-col-gutter-sm q-mb-md">
      <div class="col-6 col-md-3">
        <q-card flat bordered>
          <q-card-section class="q-pa-sm text-center">
            <div class="text-caption text-grey">Объявлений</div>
            <div class="text-h6">{{ store.total }}</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat bordered>
          <q-card-section class="q-pa-sm text-center">
            <div class="text-caption text-grey">Лучшая цена</div>
            <div class="text-h6 text-positive">{{ bestPrice }}</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat bordered>
          <q-card-section class="q-pa-sm text-center">
            <div class="text-caption text-grey">Ref. цена</div>
            <div class="text-h6">{{ store.referencePrice?.toFixed(2) ?? '—' }} ₽</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat bordered>
          <q-card-section class="q-pa-sm text-center">
            <div class="text-caption text-grey">Низкий риск</div>
            <div class="text-h6 text-positive">{{ lowRiskCount }}</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Filter Panel -->
    <filter-panel v-model="localFilters" @apply="applyFilters">
      <template #actions>
        <q-btn flat icon="save" label="Сохранить" size="sm" @click="saveDefaultFilters" />
      </template>
    </filter-panel>

    <!-- Empty State -->
    <div v-if="!store.isLoading && store.advertisements.length === 0" class="column items-center q-pa-xl text-grey">
      <q-icon name="search_off" size="4em" class="q-mb-md" />
      <div class="text-h6">Нет объявлений по заданным критериям</div>
      <div class="text-caption q-mb-md">Попробуйте изменить фильтры или выбрать другое направление</div>
      <q-btn outline label="Сбросить фильтры" @click="resetFilters" />
    </div>

    <!-- Advertisements Table -->
    <advertisement-table
      v-else
      :advertisements="store.advertisements"
      :loading="store.isLoading"
      :best-ad-id="bestAdId"
      @row-click="openCard"
    />

    <!-- Next update countdown -->
    <div v-if="!store.isLoading" class="text-center text-caption text-grey q-mt-sm">
      Следующее обновление через {{ nextUpdateIn }} сек
    </div>

    <!-- Advertisement Card Dialog -->
    <q-dialog v-model="showCard">
      <advertisement-card :advertisement="selectedAd" @close="showCard = false" @blocked="onMerchantBlocked" />
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useQuasar } from 'quasar';
import FilterPanel from 'components/FilterPanel.vue';
import AdvertisementTable from 'components/AdvertisementTable.vue';
import AdvertisementCard from 'components/AdvertisementCard.vue';
import { useAdvertisementsStore, type AdvertisementResponse } from 'stores/advertisements';
import { updateSavedFiltersApiV1ProfileFiltersPut } from 'src/api/profile/profile';
import { getSavedFiltersApiV1ProfileFiltersGet } from 'src/api/profile/profile';

const $q = useQuasar();
const store = useAdvertisementsStore();

const showCard = ref(false);
const selectedAd = ref<AdvertisementResponse | null>(null);
const direction = ref<string>('BUY');
const updateAge = ref(0);
const nextUpdateIn = ref(15);
const REFRESH_INTERVAL = 15;

const localFilters = ref({
  payment_methods: [] as string[],
  min_rating: null as number | null,
  min_trades: null as number | null,
  min_amount: null as number | null,
  max_amount: null as number | null,
});

const bestPrice = computed(() => {
  if (!store.advertisements.length) return '—';
  const prices = store.advertisements.map((a) => a.price);
  return Math.min(...prices).toFixed(2) + ' ₽';
});

const lowRiskCount = computed(() =>
  store.advertisements.filter((a) => a.risk_score != null && a.risk_score <= 3).length
);

const bestAdId = computed(() => {
  if (!store.advertisements.length) return null;
  const sorted = [...store.advertisements].sort(
    (a, b) => (b.net_yield ?? 0) - (a.net_yield ?? 0)
  );
  return sorted[0]?.id || null;
});

let refreshInterval: ReturnType<typeof setInterval> | null = null;
let tickInterval: ReturnType<typeof setInterval> | null = null;
let lastFetchTime = Date.now();

function applyFilters() {
  store.setFilters({
    payment_methods: localFilters.value.payment_methods.length ? localFilters.value.payment_methods : undefined,
    min_amount: localFilters.value.min_amount ?? undefined,
    max_amount: localFilters.value.max_amount ?? undefined,
  });
}

function resetFilters() {
  localFilters.value = { payment_methods: [], min_rating: null, min_trades: null, min_amount: null, max_amount: null };
  store.resetFilters();
}

async function saveDefaultFilters() {
  try {
    await updateSavedFiltersApiV1ProfileFiltersPut({ filters: localFilters.value });
    $q.notify({ type: 'positive', message: 'Фильтры сохранены' });
  } catch {
    $q.notify({ type: 'negative', message: 'Ошибка сохранения' });
  }
}

function openCard(ad: AdvertisementResponse) {
  selectedAd.value = ad;
  showCard.value = true;
}

function onMerchantBlocked(merchantId: string) {
  store.advertisements = store.advertisements.filter((ad) => ad.merchant.id !== merchantId);
}

function tick() {
  updateAge.value = Math.floor((Date.now() - lastFetchTime) / 1000);
  nextUpdateIn.value = Math.max(0, REFRESH_INTERVAL - updateAge.value);
}

async function refresh() {
  await store.fetchAdvertisements();
  lastFetchTime = Date.now();
  updateAge.value = 0;
}

onMounted(async () => {
  try {
    const saved = await getSavedFiltersApiV1ProfileFiltersGet();
    if (saved?.filters) {
      Object.assign(localFilters.value, saved.filters);
    }
  } catch { /* no saved filters */ }

  await refresh();
  refreshInterval = setInterval(refresh, REFRESH_INTERVAL * 1000);
  tickInterval = setInterval(tick, 1000);
});

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval);
  if (tickInterval) clearInterval(tickInterval);
});
</script>
