<template>
  <q-page padding class="flex flex-center">
    <q-card style="max-width: 600px; width: 100%">
      <q-card-section>
        <div class="text-h6">Настройка профиля</div>
        <div class="text-caption text-grey">Шаг {{ step }} из 4</div>
        <q-linear-progress :value="step / 4" class="q-mt-sm" />
      </q-card-section>

      <!-- Step 1: Banks -->
      <q-card-section v-if="step === 1">
        <div class="text-subtitle2 q-mb-md">Выберите банки и способы оплаты</div>
        <q-select
          v-model="form.payment_methods"
          :options="availableBanks"
          label="Способы оплаты"
          multiple
          outlined
          use-chips
        />
      </q-card-section>

      <!-- Step 2: Amount range -->
      <q-card-section v-if="step === 2">
        <div class="text-subtitle2 q-mb-md">Диапазон сумм сделки (₽)</div>
        <div class="row q-col-gutter-md">
          <div class="col-6">
            <q-input v-model.number="form.min_amount" label="От" type="number" outlined />
          </div>
          <div class="col-6">
            <q-input v-model.number="form.max_amount" label="До" type="number" outlined />
          </div>
        </div>
      </q-card-section>

      <!-- Step 3: Risk profile -->
      <q-card-section v-if="step === 3">
        <div class="text-subtitle2 q-mb-md">Выберите риск-профиль</div>
        <q-btn-toggle
          v-model="form.risk_profile"
          spread
          no-caps
          toggle-color="primary"
          :options="[
            { label: 'Консервативный', value: 'low' },
            { label: 'Умеренный', value: 'medium' },
            { label: 'Агрессивный', value: 'high' },
          ]"
        />
        <div class="text-caption text-grey q-mt-sm">
          <span v-if="form.risk_profile === 'low'">Показывать только мерчантов с низким риском (скор 1–3)</span>
          <span v-else-if="form.risk_profile === 'medium'">Показывать мерчантов с низким и средним риском (скор 1–7)</span>
          <span v-else>Показывать всех мерчантов без ограничений</span>
        </div>
      </q-card-section>

      <!-- Step 4: Commissions -->
      <q-card-section v-if="step === 4">
        <div class="text-subtitle2 q-mb-md">Комиссии вашего банка (опционально)</div>
        <q-input
          v-model.number="form.commission_percent"
          label="Комиссия (%)"
          type="number"
          outlined
          class="q-mb-md"
        />
        <q-input
          v-model.number="form.commission_fixed"
          label="Фиксированная комиссия (₽)"
          type="number"
          outlined
        />
        <div class="text-caption text-grey q-mt-sm">
          Можно указать позже в настройках профиля
        </div>
      </q-card-section>

      <q-card-actions align="between">
        <q-btn v-if="step > 1" flat label="Назад" @click="step--" />
        <q-space v-else />
        <div>
          <q-btn flat label="Пропустить" @click="skip" class="q-mr-sm" />
          <q-btn
            v-if="step < 4"
            color="primary"
            label="Далее"
            @click="step++"
          />
          <q-btn
            v-else
            color="primary"
            label="Завершить"
            :loading="saving"
            @click="complete"
          />
        </div>
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { useAuthStore } from 'stores/auth';

const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();

const step = ref(1);
const saving = ref(false);

const availableBanks = ['Сбербанк', 'Тинькофф', 'Альфа-Банк', 'Райффайзен', 'СБП', 'ВТБ'];

const form = ref({
  payment_methods: [] as string[],
  min_amount: null as number | null,
  max_amount: null as number | null,
  risk_profile: 'medium',
  commission_percent: null as number | null,
  commission_fixed: null as number | null,
});

async function complete() {
  saving.value = true;
  try {
    await api.post('/profile/onboarding', form.value);
    if (authStore.user) {
      authStore.user.onboarding_completed = true;
    }
    $q.notify({ type: 'positive', message: 'Профиль настроен' });
    await router.push('/');
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Ошибка сохранения' });
  } finally {
    saving.value = false;
  }
}

async function skip() {
  saving.value = true;
  try {
    await api.post('/profile/onboarding', {
      payment_methods: [],
      risk_profile: 'medium',
    });
    if (authStore.user) {
      authStore.user.onboarding_completed = true;
    }
    await router.push('/');
  } finally {
    saving.value = false;
  }
}
</script>
