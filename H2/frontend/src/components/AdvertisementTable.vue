<template>
  <q-table
    :rows="advertisements"
    :columns="columns"
    :loading="loading"
    row-key="id"
    flat bordered
    :row-class="rowClass"
    @row-click="onRowClick"
  >
    <template v-slot:body-cell-merchant="props">
      <q-td :props="props">
        <div class="row items-center no-wrap">
          <q-icon v-if="props.row.id === bestAdId" name="star" color="amber" size="xs" class="q-mr-xs" />
          {{ props.row.merchant?.name ?? '—' }}
          <q-badge v-if="props.row.merchant?.is_verified" color="blue" class="q-ml-xs" label="✓" />
        </div>
      </q-td>
    </template>

    <template v-slot:body-cell-price="props">
      <q-td :props="props">{{ props.row.price?.toFixed(2) }} ₽</q-td>
    </template>

    <template v-slot:body-cell-volume="props">
      <q-td :props="props">{{ formatAmount(props.row.volume) }}</q-td>
    </template>

    <template v-slot:body-cell-payment_methods="props">
      <q-td :props="props">
        <q-chip v-for="m in props.row.payment_methods?.slice(0, 2)" :key="m" size="sm" class="q-mr-xs">{{ m }}</q-chip>
        <q-chip v-if="(props.row.payment_methods?.length ?? 0) > 2" size="sm">+{{ props.row.payment_methods.length - 2 }}</q-chip>
      </q-td>
    </template>

    <template v-slot:body-cell-risk_score="props">
      <q-td :props="props">
        <risk-badge :score="props.row.risk_score ?? 0" :category="props.row.risk_category ?? 'medium'" />
      </q-td>
    </template>

    <template v-slot:body-cell-spread="props">
      <q-td :props="props">
        <span v-if="props.row.spread != null" :class="props.row.spread >= 0 ? 'text-negative' : 'text-positive'">
          {{ props.row.spread >= 0 ? '+' : '' }}{{ props.row.spread.toFixed(2) }}%
        </span>
        <span v-else class="text-grey">—</span>
      </q-td>
    </template>

    <template v-slot:body-cell-net_yield="props">
      <q-td :props="props">
        <profitability-tooltip :value="props.row.net_yield ?? 0" />
      </q-td>
    </template>

    <template v-slot:no-data>
      <div class="full-width row flex-center q-gutter-sm text-grey q-pa-lg">
        <q-icon name="search_off" size="2em" />
        <span>Нет объявлений</span>
      </div>
    </template>
  </q-table>
</template>

<script setup lang="ts">
import RiskBadge from 'components/RiskBadge.vue';
import ProfitabilityTooltip from 'components/ProfitabilityTooltip.vue';
import type { AdvertisementResponse } from 'src/api/client.schemas';

const props = defineProps<{
  advertisements: AdvertisementResponse[];
  loading: boolean;
  bestAdId?: string | null;
}>();

const emit = defineEmits<{
  (e: 'row-click', ad: AdvertisementResponse): void;
}>();

const columns = [
  { name: 'merchant', label: 'Мерчант', field: (r: AdvertisementResponse) => r.merchant?.name, align: 'left' as const, sortable: true },
  { name: 'price', label: 'Цена', field: 'price', align: 'right' as const, sortable: true },
  { name: 'volume', label: 'Объём', field: 'volume', align: 'right' as const, sortable: true },
  { name: 'payment_methods', label: 'Оплата', field: 'payment_methods', align: 'left' as const },
  { name: 'spread', label: 'Спред', field: 'spread', align: 'right' as const, sortable: true },
  { name: 'risk_score', label: 'Риск', field: 'risk_score', align: 'center' as const, sortable: true },
  { name: 'net_yield', label: 'Доходность', field: 'net_yield', align: 'right' as const, sortable: true },
];

function rowClass(row: AdvertisementResponse): string {
  if (row.id === props.bestAdId) return 'bg-green-1';
  return '';
}

function onRowClick(_event: Event, row: AdvertisementResponse) {
  emit('row-click', row);
}

function formatAmount(value: number | undefined): string {
  if (value === undefined) return '—';
  return new Intl.NumberFormat('ru-RU').format(value);
}
</script>
