<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">Профиль трейдера</div>

    <q-tabs v-model="tab" class="q-mb-md" align="left" no-caps active-color="primary" indicator-color="primary">
      <q-tab name="settings" icon="tune" label="Настройки торговли" />
      <q-tab name="filters" icon="filter_list" label="Фильтры по умолчанию" />
      <q-tab name="kyc" icon="verified_user" label="KYC и лимиты" />
    </q-tabs>

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="settings">
        <q-card flat bordered>
          <q-card-section>
            <q-form @submit="saveProfile" class="q-gutter-md" style="max-width: 500px">
              <q-select v-model="profile.payment_methods" :options="availableBanks" label="Мои банки" multiple outlined use-chips />
              <div class="row q-col-gutter-md">
                <div class="col-6"><q-input v-model.number="profile.min_amount" label="Мин. сумма (₽)" type="number" outlined /></div>
                <div class="col-6"><q-input v-model.number="profile.max_amount" label="Макс. сумма (₽)" type="number" outlined /></div>
              </div>
              <q-select v-model="profile.risk_profile" :options="riskProfiles" label="Риск-профиль" outlined emit-value map-options />
              <div class="row q-col-gutter-md">
                <div class="col-6"><q-input v-model.number="profile.commission_percent" label="Комиссия (%)" type="number" outlined /></div>
                <div class="col-6"><q-input v-model.number="profile.commission_fixed" label="Фикс. комиссия (₽)" type="number" outlined /></div>
              </div>
              <q-btn type="submit" color="primary" label="Сохранить" :loading="profileMutation.isPending.value" />
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <q-tab-panel name="filters">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-caption text-grey q-mb-md">Автоматически применяются при входе.</div>
            <q-form @submit="saveFilters" class="q-gutter-md" style="max-width: 500px">
              <q-select v-model="filters.payment_methods" :options="availableBanks" label="Банки" multiple outlined use-chips />
              <div class="row q-col-gutter-md">
                <div class="col-6"><q-input v-model.number="filters.min_rating" label="Мин. рейтинг" type="number" outlined /></div>
                <div class="col-6"><q-input v-model.number="filters.min_trades" label="Мин. сделок" type="number" outlined /></div>
              </div>
              <div class="row q-col-gutter-md">
                <div class="col-6"><q-input v-model.number="filters.min_amount" label="Сумма от (₽)" type="number" outlined /></div>
                <div class="col-6"><q-input v-model.number="filters.max_amount" label="Сумма до (₽)" type="number" outlined /></div>
              </div>
              <q-btn type="submit" color="primary" label="Сохранить фильтры" :loading="filtersMutation.isPending.value" />
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <q-tab-panel name="kyc">
        <q-card flat bordered>
          <q-card-section>
            <q-form @submit="saveProfile" class="q-gutter-md" style="max-width: 500px">
              <q-select v-model="profile.kyc_level" :options="kycLevels" label="KYC-уровень" outlined emit-value map-options clearable />
              <q-select v-model="profile.country" :options="countries" label="Страна" outlined emit-value map-options />
              <q-input v-model.number="profile.kyc_limit_warning" label="Порог предупреждения (₽)" type="number" outlined />
              <q-btn type="submit" color="primary" label="Сохранить" :loading="profileMutation.isPending.value" />
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import {
  getProfileApiV1ProfileGet,
  getSavedFiltersApiV1ProfileFiltersGet,
  useUpdateProfileApiV1ProfilePut,
  useUpdateSavedFiltersApiV1ProfileFiltersPut,
} from 'src/api/profile/profile';

const $q = useQuasar();
const tab = ref('settings');

const availableBanks = ['Сбербанк', 'Тинькофф', 'Альфа-Банк', 'Райффайзен', 'СБП', 'ВТБ'];
const riskProfiles = [
  { label: 'Консервативный', value: 'low' },
  { label: 'Умеренный', value: 'medium' },
  { label: 'Агрессивный', value: 'high' },
];
const kycLevels = [
  { label: 'Не пройден', value: 'none' },
  { label: 'Базовый', value: 'basic' },
  { label: 'Расширенный', value: 'advanced' },
  { label: 'Полный', value: 'full' },
];
const countries = [
  { label: 'Россия', value: 'RU' },
  { label: 'Казахстан', value: 'KZ' },
  { label: 'Беларусь', value: 'BY' },
];

const profile = ref<Record<string, unknown>>({
  payment_methods: [], min_amount: null, max_amount: null,
  risk_profile: 'medium', commission_percent: null, commission_fixed: null,
  kyc_level: null, country: 'RU', kyc_limit_warning: null,
});

const filters = ref<Record<string, unknown>>({
  payment_methods: [], min_rating: null, min_trades: null, min_amount: null, max_amount: null,
});

const profileMutation = useUpdateProfileApiV1ProfilePut({
  mutation: {
    onSuccess: () => $q.notify({ type: 'positive', message: 'Профиль сохранён' }),
    onError: () => $q.notify({ type: 'negative', message: 'Ошибка сохранения' }),
  },
});

const filtersMutation = useUpdateSavedFiltersApiV1ProfileFiltersPut({
  mutation: {
    onSuccess: () => $q.notify({ type: 'positive', message: 'Фильтры сохранены' }),
    onError: () => $q.notify({ type: 'negative', message: 'Ошибка сохранения' }),
  },
});

function saveProfile() {
  profileMutation.mutate({ data: profile.value as never });
}

function saveFilters() {
  filtersMutation.mutate({ data: { filters: filters.value as never } });
}

onMounted(async () => {
  try {
    const p = await getProfileApiV1ProfileGet();
    Object.assign(profile.value, p);
  } catch { /* defaults */ }
  try {
    const f = await getSavedFiltersApiV1ProfileFiltersGet();
    if (f?.filters) Object.assign(filters.value, f.filters);
  } catch { /* defaults */ }
});
</script>
