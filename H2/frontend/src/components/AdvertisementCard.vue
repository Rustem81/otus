<template>
  <q-card style="min-width: 400px; max-width: 500px">
    <q-card-section class="row items-center">
      <div class="text-h6">{{ advertisement?.merchant_name }}</div>
      <q-space />
      <q-btn icon="close" flat round dense v-close-popup />
    </q-card-section>

    <q-card-section>
      <div class="row q-col-gutter-md">
        <div class="col-6">
          <div class="text-caption text-grey">Цена</div>
          <div class="text-h6">{{ formatPrice(advertisement?.price) }} ₽</div>
        </div>
        <div class="col-6">
          <div class="text-caption text-grey">Доступно</div>
          <div class="text-h6">{{ formatAmount(advertisement?.available_amount) }} ₽</div>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div class="row q-col-gutter-md">
        <div class="col-6">
          <div class="text-caption text-grey">Мин. сумма</div>
          <div>{{ formatAmount(advertisement?.min_amount) }} ₽</div>
        </div>
        <div class="col-6">
          <div class="text-caption text-grey">Макс. сумма</div>
          <div>{{ formatAmount(advertisement?.max_amount) }} ₽</div>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div>
        <div class="text-caption text-grey q-mb-sm">Способы оплаты</div>
        <div class="row q-gutter-xs">
          <q-chip
            v-for="method in advertisement?.payment_methods"
            :key="method"
            size="sm"
          >
            {{ method }}
          </q-chip>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div class="row q-col-gutter-md items-center">
        <div class="col-6">
          <div class="text-caption text-grey">Риск-скор</div>
          <risk-badge
            :score="advertisement?.risk_score || 0"
            :category="advertisement?.risk_category || 'medium'"
          />
        </div>
        <div class="col-6">
          <div class="text-caption text-grey">Доходность</div>
          <profitability-tooltip :value="advertisement?.profitability || 0" />
        </div>
      </div>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn
        color="primary"
        label="Открыть в MEXC"
        @click="openMexc"
        target="_blank"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import RiskBadge from 'components/RiskBadge.vue';
import ProfitabilityTooltip from 'components/ProfitabilityTooltip.vue';
import type { Advertisement } from 'src/api/advertisements';

defineProps<{
  advertisement: Advertisement | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

function formatPrice(value: number | undefined): string {
  return value?.toFixed(2) || '-';
}

function formatAmount(value: number | undefined): string {
  if (value === undefined) return '-';
  return new Intl.NumberFormat('ru-RU').format(value);
}

function openMexc() {
  window.open('https://www.mexc.com/ru-RU/p2p', '_blank');
  emit('close');
}
</script>
