<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">Профиль трейдера</div>

    <q-tabs v-model="tab" class="q-mb-md" align="left" no-caps active-color="primary" indicator-color="primary">
      <q-tab name="settings" icon="tune" label="Настройки торговли" />
      <q-tab name="filters" icon="filter_list" label="Фильтры по умолчанию" />
      <q-tab name="kyc" icon="verified_user" label="KYC и лимиты" />
    </q-tabs>

    <q-tab-panels v-model="tab" animated>
      <!-- Trading Settings -->
      <q-tab-panel name="settings">
        <q-card flat bordered>
          <q-card-section>
            <q-form @submit="saveProfile" class="q-gutter-md" style="max-width: 500px">
              <q-select
                v-model="profile.payment_methods"
                :options="availableBanks"
                label="Мои банки и способы оплаты"
                multiple outlined use-chips
                hint="Объявления будут фильтроваться по выбранным банкам"
              />
              <div class="row q-col-gutter-md">
                <div class="col-6">
                  <q-input v-model.number="profile.min_amount" label="Мин. сумма (₽)" type="number" outlined />
                </div>
                <div class="col-6">
                  <q-input v-model.number="profile.max_amount" label="Макс. сумма (₽)" type="number" outlined />
                </div>
              </div>
              <q-select
                v-model="profile.risk_profile"
                :options="riskProfiles"
                label="Риск-профиль"
                outlined emit-value map-options
                hint="Влияет на сортировку и подсветку объявлений"
              />
              <div class="row q-col-gutter-md">
                <div class="col-6">
                  <q-input v-model.number="profile.commission_percent" label="Комиссия банка (%)" type="number" outlined />
                </div>
                <div class="col-6">
                  <q-input v-model.number="profile.commission_fixed" label="Фикс. комиссия (₽)" type="number" outlined />
                </div>
              </div>
              <q-btn type="submit" color="primary" label="Сохранить" :loading="saving" />
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <!-- Default Filters -->
      <q-tab-panel name="filters">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-caption text-grey q-mb-md">
              Эти фильтры будут автоматически применяться при входе в систему.
            </div>
            <q-form @submit="saveFilters" class="q-gutter-md" style="max-width: 500px">
              <q-select
                v-model="filters.payment_methods"
                :options="availableBanks"
                label="Банки" multiple outlined use-chips
              />
              <div class="row q-col-gutter-md">
                <div class="col-6">
                  <q-input v-model.number="filters.min_rating" label="Мин. рейтинг" type="number" outlined min="0" max="5" />
                </div>
                <div class="col-6">
                  <q-input v-model.number="filters.min_trades" label="Мин. сделок" type="number" outlined />
                </div>
              </div>
              <div class="row q-col-gutter-md">
                <div class="col-6">
                  <q-input v-model.number="filters.min_amount" label="Сумма от (₽)" type="number" outlined />
                </div>
                <div class="col-6">
                  <q-input v-model.number="filters.max_amount" label="Сумма до (₽)" type="number" outlined />
                </div>
              </div>
              <q-btn type="submit" color="primary" label="Сохранить фильтры" :loading="savingFilters" />
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <!-- KYC -->
      <q-tab-panel name="kyc">
        <q-card flat bordered>
          <q-card-section>
            <q-form @submit="saveProfile" class="q-gutter-md" style="max-width: 500px">
              <q-select
                v-model="profile.kyc_level"
                :options="kycLevels"
                label="KYC-уровень" outlined emit-value map-options clearable
              />
              <q-select
                v-model="profile.country"
                :options="countries"
                label="Страна" outlined emit-value map-options
              />
              <q-input
                v-model.number="profile.kyc_limit_warning"
                label="Порог предупреждения о лимите (₽)"
                type="number" outlined
                hint="Вы получите предупреждение при приближении к этой сумме"
              />
              <q-btn type="submit" color="primary" label="Сохранить" :loading="saving" />
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
import { api } from 'boot/axios';

const $q = useQuasar();
const tab = ref('settings');

interface Profile {
  payment_methods: string[];
  min_amount: number | null;
  max_amount: number | null;
  risk_profile: string;
  commission_percent: number | null;
  commission_fixed: number | null;
  kyc_level: string | null;
  country: string | null;
  kyc_limit_warning: number | null;
}

interface Filters {
  payment_methods: string[];
  min_rating: number | null;
  min_trades: number | null;
  min_amount: number | null;
  max_amount: number | null;
}

const availableBanks = ['Сбербанк', 'Тинькофф', 'Альфа-Банк', 'Райффайзен', 'СБП', 'ВТБ'];
const riskProfiles = [
  { label: 'Консервативный (низкий риск)', value: 'low' },
  { label: 'Умеренный', value: 'medium' },
  { label: 'Агрессивный (высокий риск)', value: 'high' },
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
  { label: 'Узбекистан', value: 'UZ' },
];

const profile = ref<Profile>({
  payment_methods: [], min_amount: null, max_amount: null,
  risk_profile: 'medium', commission_percent: null, commission_fixed: null,
  kyc_level: null, country: 'RU', kyc_limit_warning: null,
});
const filters = ref<Filters>({
  payment_methods: [], min_rating: null, min_trades: null, min_amount: null, max_amount: null,
});
const saving = ref(false);
const savingFilters = ref(false);

async function saveProfile() {
  saving.value = true;
  try {
    await api.put('/profile/', profile.value);
    $q.notify({ type: 'positive', message: 'Профиль сохранён' });
  } catch {
    $q.notify({ type: 'negative', message: 'Ошибка сохранения' });
  } finally {
    saving.value = false;
  }
}

async function saveFilters() {
  savingFilters.value = true;
  try {
    await api.put('/profile/filters', { filters: filters.value });
    $q.notify({ type: 'positive', message: 'Фильтры сохранены' });
  } catch {
    $q.notify({ type: 'negative', message: 'Ошибка сохранения' });
  } finally {
    savingFilters.value = false;
  }
}

onMounted(async () => {
  try {
    const [profileResp, filtersResp] = await Promise.all([
      api.get('/profile/'),
      api.get('/profile/filters'),
    ]);
    Object.assign(profile.value, profileResp.data);
    if (filtersResp.data?.filters) {
      Object.assign(filters.value, filtersResp.data.filters);
    }
  } catch { /* defaults */ }
});
</script>
