import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  getAdvertisements,
  type Advertisement,
  type AdvertisementsFilters,
} from 'src/api/advertisements';

export const useAdvertisementsStore = defineStore('advertisements', () => {
  const advertisements = ref<Advertisement[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(20);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const filters = ref<AdvertisementsFilters>({});

  const hasMore = computed(() => advertisements.value.length < total.value);

  async function fetchAdvertisements(reset = true) {
    if (isLoading.value) return;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await getAdvertisements({
        ...filters.value,
        page: reset ? 1 : page.value,
        page_size: pageSize.value,
      });

      if (reset) {
        advertisements.value = response.items;
        page.value = 1;
      } else {
        advertisements.value.push(...response.items);
      }

      total.value = response.total;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch advertisements';
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMore() {
    if (!hasMore.value || isLoading.value) return;
    page.value++;
    await fetchAdvertisements(false);
  }

  function setFilters(newFilters: AdvertisementsFilters) {
    filters.value = newFilters;
    fetchAdvertisements(true);
  }

  function resetFilters() {
    filters.value = {};
    fetchAdvertisements(true);
  }

  return {
    advertisements,
    total,
    page,
    pageSize,
    isLoading,
    error,
    filters,
    hasMore,
    fetchAdvertisements,
    loadMore,
    setFilters,
    resetFilters,
  };
});
