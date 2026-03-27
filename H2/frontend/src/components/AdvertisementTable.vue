<template>
  <q-table
    :rows="advertisements"
    :columns="columns"
    :loading="loading"
    row-key="id"
    flat
    bordered
    @row-click="onRowClick"
  >
    <template v-slot:body-cell-risk_score="props">
      <q-td :props="props">
        <risk-badge
          :score="props.row.risk_score"
          :category="props.row.risk_category"
        />
      </q-td>
    </template>

    <template v-slot:body-cell-price="props">
      <q-td :props="props">
        {{ formatPrice(props.row.price) }} ₽
      </q-td>
    </template>

    <template v-slot:body-cell-available_amount="props">
      <q-td :props="props">
        {{ formatAmount(props.row.available_amount) }} ₽
      </q-td>
    </template>

    <template v-slot:body-cell-payment_methods="props">
      <q-td :props="props">
        <q-chip
          v-for="method in props.row.payment_methods.slice(0, 2)"
          :key="method"
          size="sm"
          class="q-mr-xs"
        >
          {{ method }}
        </q-chip>
        <q-chip
          v-if="props.row.payment_methods.length > 2"
          size="sm"
          class="q-mr-xs"
        >
          +{{ props.row.payment_methods.length - 2 }}
        </q-chip>
      </q-td>
    </template>

    <template v-slot:body-cell-profitability="props">
      <q-td :props="props">
        <profitability-tooltip :value="props.row.profitability" />
      </q-td>
    </template>
  </q-table>
</template>

<script setup lang="ts">
import RiskBadge from 'components/RiskBadge.vue';
import ProfitabilityTooltip from 'components/ProfitabilityTooltip.vue';
import type { Advertisement } from 'src/api/advertisements';

defineProps<{
  advertisements: Advertisement[];
  loading: boolean;
}>();

const emit = defineEmits<{
  (e: 'row-click', ad: Advertisement): void;
}>();

const columns = [
  {
    name: 'merchant_name',
    label: 'Мерчант',
    field: 'merchant_name',
    align: 'left',
    sortable: true,
  },
  {
    name: 'price',
    label: 'Цена',
    field: 'price',
    align: 'right',
    sortable: true,
  },
  {
    name: 'available_amount',
    label: 'Доступно',
    field: 'available_amount',
    align: 'right',
    sortable: true,
  },
  {
    name: 'payment_methods',
    label: 'Способы оплаты',
    field: 'payment_methods',
    align: 'left',
  },
  {
    name: 'risk_score',
    label: 'Риск',
    field: 'risk_score',
    align: 'center',
    sortable: true,
  },
  {
    name: 'profitability',
    label: 'Доходность',
    field: 'profitability',
    align: 'right',
    sortable: true,
  },
];

function onRowClick(_event: Event, row: Advertisement) {
  emit('row-click', row);
}

function formatPrice(value: number): string {
  return value.toFixed(2);
}

function formatAmount(value: number): string {
  return new Intl.NumberFormat('ru-RU').format(value);
}
</script>
