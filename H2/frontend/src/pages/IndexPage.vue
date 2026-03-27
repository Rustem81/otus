<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h6">P2P Объявления</div>
      <q-space />
      <q-btn
        flat
        round
        icon="refresh"
        :loading="store.isLoading"
        @click="store.fetchAdvertisements()"
      >
        <q-tooltip>Обновить</q-tooltip>
      </q-btn>
    </div>

    <!-- Error Banner -->
    <q-banner
      v-if="store.error"
      class="bg-negative text-white q-mb-md"
      rounded
    >
      <template #avatar>
        <q-icon name="error" />
      </template>
      {{ store.error }}
      <template #action>
        <q-btn flat label="Повторить" @click="store.fetchAdvertisements()" />
      </template>
    </q-banner>

    <!-- Filter Panel -->
    <filter-panel v-model="localFilters" @apply="applyFilters" />

    <!-- Advertisements Table -->
    <advertisement-table
      :advertisements="store.advertisements"
      :loading="store.isLoading"
      @row-click="openCard"
    />

    <!-- Load More Button -->
    <div v-if="store.hasMore && !store.isLoading" class="row justify-center q-mt-md">
      <q-btn
        outline
        label="Загрузить ещё"
        @click="store.loadMore()"
      />
    </div>

    <!-- Advertisement Card Dialog -->
    <q-dialog v-model="showCard" persistent>
      <advertisement-card
        :advertisement="selectedAd"
        @close="showCard = false"
      />
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import FilterPanel from 'components/FilterPanel.vue';
import AdvertisementTable from 'components/AdvertisementTable.vue';
import AdvertisementCard from 'components/AdvertisementCard.vue';
import { useAdvertisementsStore } from 'stores/advertisements';
import type { Advertisement } from 'src/api/advertisements';

const store = useAdvertisementsStore();

const showCard = ref(false);
const selectedAd = ref<Advertisement | null>(null);

const localFilters = ref({
  payment_methods: [] as string[],
  min_rating: null as number | null,
  min_trades: null as number | null,
  min_amount: null as number | null,
  max_amount: null as number | null,
});

let refreshInterval: ReturnType<typeof setInterval> | null = null;

function applyFilters() {
  store.setFilters({
    payment_methods: localFilters.value.payment_methods,
    min_rating: localFilters.value.min_rating ?? undefined,
    min_trades: localFilters.value.min_trades ?? undefined,
    min_amount: localFilters.value.min_amount ?? undefined,
    max_amount: localFilters.value.max_amount ?? undefined,
  });
}

function openCard(ad: Advertisement) {
  selectedAd.value = ad;
  showCard.value = true;
}

onMounted(() => {
  store.fetchAdvertisements();
  refreshInterval = setInterval(() => store.fetchAdvertisements(), 30000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>
