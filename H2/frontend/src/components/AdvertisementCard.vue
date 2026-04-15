<template>
  <q-card style="min-width: 400px; max-width: 500px">
    <q-card-section class="row items-center">
      <div class="text-h6">{{ advertisement?.merchant?.name }}</div>
      <q-space />
      <q-btn icon="close" flat round dense v-close-popup />
    </q-card-section>

    <q-card-section>
      <div class="row q-col-gutter-md">
        <div class="col-6">
          <div class="text-caption text-grey">Цена</div>
          <div class="text-h6">{{ advertisement?.price?.toFixed(2) ?? '—' }} ₽</div>
        </div>
        <div class="col-6">
          <div class="text-caption text-grey">Объём</div>
          <div class="text-h6">{{ formatAmount(advertisement?.volume) }}</div>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div class="row q-col-gutter-md">
        <div class="col-6">
          <div class="text-caption text-grey">Мин. сумма</div>
          <div>{{ formatAmount(advertisement?.min_limit) }} ₽</div>
        </div>
        <div class="col-6">
          <div class="text-caption text-grey">Макс. сумма</div>
          <div>{{ formatAmount(advertisement?.max_limit) }} ₽</div>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div>
        <div class="text-caption text-grey q-mb-sm">Способы оплаты</div>
        <div class="row q-gutter-xs">
          <q-chip v-for="method in advertisement?.payment_methods" :key="method" size="sm">{{ method }}</q-chip>
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div class="row q-col-gutter-md items-center">
        <div class="col-4">
          <div class="text-caption text-grey">Риск</div>
          <risk-badge :score="advertisement?.risk_score ?? 0" :category="advertisement?.risk_category ?? 'medium'" />
        </div>
        <div class="col-4">
          <div class="text-caption text-grey">Спред</div>
          <span :class="(advertisement?.spread ?? 0) >= 0 ? 'text-negative' : 'text-positive'">
            {{ advertisement?.spread != null ? advertisement.spread.toFixed(2) + '%' : '—' }}
          </span>
        </div>
        <div class="col-4">
          <div class="text-caption text-grey">Доходность</div>
          <profitability-tooltip :value="advertisement?.net_yield ?? 0" />
        </div>
      </div>

      <q-separator class="q-my-md" />

      <div class="row q-col-gutter-md">
        <div class="col-4">
          <div class="text-caption text-grey">Рейтинг</div>
          <div>{{ advertisement?.merchant?.rating?.toFixed(1) ?? '—' }} / 5</div>
        </div>
        <div class="col-4">
          <div class="text-caption text-grey">Сделок</div>
          <div>{{ advertisement?.merchant?.trades_count ?? '—' }}</div>
        </div>
        <div class="col-4">
          <div class="text-caption text-grey">Успешных</div>
          <div>{{ advertisement?.merchant?.success_rate != null ? (advertisement.merchant.success_rate * 100).toFixed(0) + '%' : '—' }}</div>
        </div>
      </div>
    </q-card-section>

    <q-card-actions align="between">
      <q-btn flat icon="block" color="negative" label="Заблокировать"
        :loading="blockMutation.isPending.value" @click="blockMerchant" />
      <q-btn color="primary" label="Открыть в MEXC" @click="openMexc" />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { useQuasar } from 'quasar';
import RiskBadge from 'components/RiskBadge.vue';
import ProfitabilityTooltip from 'components/ProfitabilityTooltip.vue';
import { useAddToBlacklistApiV1BlacklistPost } from 'src/api/blacklist/blacklist';
import { recordViewApiV1HistoryPost } from 'src/api/history/history';
import type { AdvertisementResponse } from 'src/api/client.schemas';

const $q = useQuasar();

const props = defineProps<{
  advertisement: AdvertisementResponse | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'blocked', merchantId: string): void;
}>();

const blockMutation = useAddToBlacklistApiV1BlacklistPost({
  mutation: {
    onSuccess: () => {
      $q.notify({ type: 'positive', message: 'Мерчант заблокирован' });
      if (props.advertisement) emit('blocked', props.advertisement.merchant.id);
      emit('close');
    },
    onError: () => {
      $q.notify({ type: 'negative', message: 'Ошибка блокировки' });
    },
  },
});

// Record view when card opens
watch(() => props.advertisement, async (ad) => {
  if (ad?.id) {
    try { await recordViewApiV1HistoryPost({ advertisement_id: ad.id }); } catch { /* silent */ }
  }
}, { immediate: true });

function blockMerchant() {
  if (!props.advertisement) return;
  blockMutation.mutate({ data: { merchant_id: props.advertisement.merchant.id } });
}

function formatAmount(value: number | undefined): string {
  if (value === undefined) return '—';
  return new Intl.NumberFormat('ru-RU').format(value);
}

function openMexc() {
  window.open('https://www.mexc.com/ru-RU/p2p', '_blank');
  emit('close');
}
</script>
