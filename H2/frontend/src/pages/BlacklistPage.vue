<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <q-icon name="block" size="md" class="q-mr-sm text-negative" />
      <div class="text-h6">Чёрный список мерчантов</div>
      <q-space />
      <q-chip icon="info" size="sm" color="grey-3">Объявления скрыты из таблицы</q-chip>
    </div>

    <div v-if="isLoading" class="column items-center q-pa-xl">
      <q-spinner-dots size="40px" color="primary" />
    </div>

    <q-card v-else-if="!blacklist?.items?.length" flat bordered class="q-pa-xl text-center">
      <q-icon name="check_circle" size="4em" color="positive" />
      <div class="text-h6 text-grey q-mt-md">Чёрный список пуст</div>
      <div class="text-caption text-grey q-mb-md">Заблокируйте мерчанта из карточки объявления</div>
      <q-btn outline color="primary" label="К объявлениям" to="/" icon="arrow_back" />
    </q-card>

    <div v-else class="row q-col-gutter-md">
      <div v-for="entry in blacklist.items" :key="entry.merchant_id" class="col-12 col-sm-6 col-md-4">
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center">
              <q-avatar color="negative" text-color="white" icon="person_off" size="md" class="q-mr-sm" />
              <div>
                <div class="text-subtitle2">{{ entry.merchant_id.slice(0, 12) }}...</div>
                <div class="text-caption text-grey">{{ formatDate(entry.created_at) }}</div>
              </div>
            </div>
          </q-card-section>
          <q-card-actions>
            <q-btn flat color="positive" label="Разблокировать" icon="lock_open" size="sm"
              :loading="removeMutation.isPending.value"
              @click="removeMerchant(entry.merchant_id)" />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { useQueryClient } from '@tanstack/vue-query';
import {
  useGetBlacklistApiV1BlacklistGet,
  useRemoveFromBlacklistApiV1BlacklistMerchantIdDelete,
  getGetBlacklistApiV1BlacklistGetQueryKey,
} from 'src/api/blacklist/blacklist';

const $q = useQuasar();
const queryClient = useQueryClient();

const { data: blacklist, isLoading } = useGetBlacklistApiV1BlacklistGet();

const removeMutation = useRemoveFromBlacklistApiV1BlacklistMerchantIdDelete({
  mutation: {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getGetBlacklistApiV1BlacklistGetQueryKey() });
      $q.notify({ type: 'positive', message: 'Мерчант разблокирован' });
    },
    onError: () => {
      $q.notify({ type: 'negative', message: 'Ошибка удаления' });
    },
  },
});

function removeMerchant(merchantId: string) {
  removeMutation.mutate({ merchantId });
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('ru-RU');
}
</script>
