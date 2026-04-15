import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { listAdvertisementsApiV1AdvertisementsGet } from 'src/api/advertisements/advertisements';
import type {
  AdvertisementResponse,
  ListAdvertisementsApiV1AdvertisementsGetParams,
  Direction,
} from 'src/api/client.schemas';

export type { AdvertisementResponse };

export const useAdvertisementsStore = defineStore('advertisements', () => {
  const advertisements = ref<AdvertisementResponse[]>([]);
  const total = ref(0);
  const referencePrice = ref<number | null>(null);
  const lastUpdated = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const filters = ref<ListAdvertisementsApiV1AdvertisementsGetParams>({
    currency: 'RUB',
    direction: 'BUY' as Direction,
    limit: 200,
  });

  const hasMore = computed(() => false); // All loaded at once with limit=200

  async function fetchAdvertisements() {
    if (isLoading.value) return;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await listAdvertisementsApiV1AdvertisementsGet(filters.value);
      advertisements.value = response.items;
      total.value = response.total;
      referencePrice.value = response.reference_price ?? null;
      lastUpdated.value = response.last_updated ?? null;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Ошибка загрузки объявлений';
    } finally {
      isLoading.value = false;
    }
  }

  function setFilters(newFilters: Partial<ListAdvertisementsApiV1AdvertisementsGetParams>) {
    filters.value = { ...filters.value, ...newFilters };
    fetchAdvertisements();
  }

  function setDirection(dir: Direction) {
    filters.value.direction = dir;
    fetchAdvertisements();
  }

  function resetFilters() {
    filters.value = { currency: 'RUB', direction: filters.value.direction, limit: 200 };
    fetchAdvertisements();
  }

  return {
    advertisements,
    total,
    referencePrice,
    lastUpdated,
    isLoading,
    error,
    filters,
    hasMore,
    fetchAdvertisements,
    setFilters,
    setDirection,
    resetFilters,
  };
});
