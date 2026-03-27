<template>
  <q-card class="q-mb-md">
    <q-card-section>
      <div class="row items-center">
        <div class="text-subtitle1">Фильтры</div>
        <q-space />
        <q-btn flat icon="expand_more" @click="expanded = !expanded">
          {{ expanded ? 'Свернуть' : 'Развернуть' }}
        </q-btn>
      </div>
    </q-card-section>

    <q-slide-transition>
      <div v-show="expanded">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-3">
              <q-select
                :model-value="modelValue.payment_methods"
                @update:model-value="updateFilter('payment_methods', $event)"
                :options="availableBanks"
                label="Банки"
                multiple
                outlined
                dense
                use-chips
              />
            </div>

            <div class="col-12 col-md-3">
              <q-input
                :model-value="modelValue.min_rating"
                @update:model-value="updateFilter('min_rating', $event)"
                label="Мин. рейтинг"
                type="number"
                outlined
                dense
                min="0"
                max="5"
              />
            </div>

            <div class="col-12 col-md-3">
              <q-input
                :model-value="modelValue.min_trades"
                @update:model-value="updateFilter('min_trades', $event)"
                label="Мин. сделок"
                type="number"
                outlined
                dense
              />
            </div>

            <div class="col-12 col-md-3">
              <div class="row q-col-gutter-sm">
                <div class="col-6">
                  <q-input
                    :model-value="modelValue.min_amount"
                    @update:model-value="updateFilter('min_amount', $event)"
                    label="Сумма от"
                    type="number"
                    outlined
                    dense
                  />
                </div>
                <div class="col-6">
                  <q-input
                    :model-value="modelValue.max_amount"
                    @update:model-value="updateFilter('max_amount', $event)"
                    label="Сумма до"
                    type="number"
                    outlined
                    dense
                  />
                </div>
              </div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Сбросить" @click="resetFilters" />
          <q-btn color="primary" label="Применить" @click="applyFilters" />
        </q-card-actions>
      </div>
    </q-slide-transition>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Filters {
  payment_methods: string[];
  min_rating: number | null;
  min_trades: number | null;
  min_amount: number | null;
  max_amount: number | null;
}

const props = defineProps<{
  modelValue: Filters;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: Filters): void;
  (e: 'apply'): void;
}>();

const expanded = ref(false);

const availableBanks = ['Сбербанк', 'Тинькофф', 'Альфа-Банк', 'Райффайзен', 'СБП'];

function updateFilter<K extends keyof Filters>(key: K, value: Filters[K]) {
  emit('update:modelValue', { ...props.modelValue, [key]: value });
}

function resetFilters() {
  emit('update:modelValue', {
    payment_methods: [],
    min_rating: null,
    min_trades: null,
    min_amount: null,
    max_amount: null,
  });
  emit('apply');
}

function applyFilters() {
  emit('apply');
}
</script>
