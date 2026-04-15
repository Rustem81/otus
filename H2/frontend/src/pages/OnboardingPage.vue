<template>
  <q-page padding class="flex flex-center">
    <q-card style="max-width: 600px; width: 100%">
      <q-card-section>
        <div class="text-h6">Настройка профиля</div>
        <div class="text-caption text-grey">Шаг {{ step }} из 4</div>
        <q-linear-progress :value="step / 4" class="q-mt-sm" />
      </q-card-section>

      <q-card-section v-if="step === 1">
        <div class="text-subtitle2 q-mb-md">Выберите банки и способы оплаты</div>
        <q-select v-model="form.payment_methods" :options="availableBanks" label="Способы оплаты" multiple outlined use-chips />
      </q-card-section>

      <q-card-section v-if="step === 2">
        <div class="text-subtitle2 q-mb-md">Диапазон сумм сделки (₽)</div>
        <div class="row q-col-gutter-md">
          <div class="col-6"><q-input v-model.number="form.min_amount" label="От" type="number" outlined /></div>
          <div class="col-6"><q-input v-model.number="form.max_amount" label="До" type="number" outlined /></div>
        </div>
      </q-card-section>

      <q-card-section v-if="step === 3">
        <div class="text-subtitle2 q-mb-md">Выберите риск-профиль</div>
        <q-btn-toggle v-model="form.risk_profile" spread no-caps toggle-color="primary"
          :options="[
            { label: 'Консервативный', value: 'low' },
            { label: 'Умеренный', value: 'medium' },
            { label: 'Агрессивный', value: 'high' },
          ]" />
      </q-card-section>

      <q-card-section v-if="step === 4">
        <div class="text-subtitle2 q-mb-md">Комиссии вашего банка (опционально)</div>
        <q-input v-model.number="form.commission_percent" label="Комиссия (%)" type="number" outlined class="q-mb-md" />
        <q-input v-model.number="form.commission_fixed" label="Фиксированная комиссия (₽)" type="number" outlined />
      </q-card-section>

      <q-card-actions align="between">
        <q-btn v-if="step > 1" flat label="Назад" @click="step--" />
        <q-space v-else />
        <div>
          <q-btn flat label="Пропустить" @click="skip" class="q-mr-sm" />
          <q-btn v-if="step < 4" color="primary" label="Далее" @click="step++" />
          <q-btn v-else color="primary" label="Завершить" :loading="mutation.isPending.value" @click="complete" />
        </div>
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useCompleteOnboardingApiV1ProfileOnboardingPost } from 'src/api/profile/profile';
import { useAuthStore } from 'stores/auth';

const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();
const step = ref(1);

const availableBanks = ['Сбербанк', 'Тинькофф', 'Альфа-Банк', 'Райффайзен', 'СБП', 'ВТБ'];

const form = ref({
  payment_methods: [] as string[],
  min_amount: null as number | null,
  max_amount: null as number | null,
  risk_profile: 'medium' as string,
  commission_percent: null as number | null,
  commission_fixed: null as number | null,
});

const mutation = useCompleteOnboardingApiV1ProfileOnboardingPost({
  mutation: {
    onSuccess: () => {
      if (authStore.user) {
        (authStore.user as Record<string, unknown>).onboarding_completed = true;
      }
      localStorage.setItem('onboarding_completed', 'true');
      $q.notify({ type: 'positive', message: 'Профиль настроен' });
      router.push('/');
    },
    onError: () => {
      $q.notify({ type: 'negative', message: 'Ошибка сохранения' });
    },
  },
});

function complete() {
  mutation.mutate({ data: form.value as never });
}

function skip() {
  mutation.mutate({ data: { payment_methods: [], risk_profile: 'medium' } as never });
}
</script>
