<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">Профиль трейдера</div>

    <div class="row q-col-gutter-md">
      <!-- Profile Settings -->
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-subtitle1">Настройки</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit="saveProfile" class="q-gutter-md">
              <q-select
                v-model="profile.payment_methods"
                :options="availableBanks"
                label="Способы оплаты"
                multiple
                outlined
                use-chips
              />

              <q-input
                v-model.number="profile.min_amount"
                label="Мин. сумма (₽)"
                type="number"
                outlined
              />

              <q-input
                v-model.number="profile.max_amount"
                label="Макс. сумма (₽)"
                type="number"
                outlined
              />

              <q-select
                v-model="profile.risk_profile"
                :options="riskProfiles"
                label="Риск-профиль"
                outlined
                emit-value
                map-options
              />

              <q-input
                v-model.number="profile.commission_percent"
                label="Комиссия (%)"
                type="number"
                outlined
              />

              <q-input
                v-model.number="profile.commission_fixed"
                label="Фикс. комиссия (₽)"
                type="number"
                outlined
              />

              <q-btn
                type="submit"
                color="primary"
                label="Сохранить"
                :loading="saving"
              />
            </q-form>
          </q-card-section>
        </q-card>
      </div>

      <!-- Saved Filters -->
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-subtitle1">Сохранённые фильтры</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit="saveFilters" class="q-gutter-md">
              <q-select
                v-model="filters.payment_methods"
                :options="availableBanks"
                label="Банки"
                multiple
                outlined
                use-chips
              />

              <q-input
                v-model.number="filters.min_rating"
                label="Мин. рейтинг"
                type="number"
                outlined
                min="0"
                max="5"
              />

              <q-input
                v-model.number="filters.min_trades"
                label="Мин. сделок"
                type="number"
                outlined
              />

              <q-input
                v-model.number="filters.min_amount"
                label="Мин. сумма"
                type="number"
                outlined
              />

              <q-input
                v-model.number="filters.max_amount"
                label="Макс. сумма"
                type="number"
                outlined
              />

              <q-btn
                type="submit"
                color="primary"
                label="Сохранить фильтры"
                :loading="savingFilters"
              />
            </q-form>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

interface Profile {
  payment_methods: string[];
  min_amount: number | null;
  max_amount: number | null;
  risk_profile: string;
  commission_percent: number | null;
  commission_fixed: number | null;
}

interface Filters {
  payment_methods: string[];
  min_rating: number | null;
  min_trades: number | null;
  min_amount: number | null;
  max_amount: number | null;
}

const availableBanks = ['Сбербанк', 'Тинькофф', 'Альфа-Банк', 'Райффайзен', 'СБП'];

const riskProfiles = [
  { label: 'Консервативный', value: 'conservative' },
  { label: 'Средний', value: 'medium' },
  { label: 'Агрессивный', value: 'aggressive' },
];

const profile = ref<Profile>({
  payment_methods: [],
  min_amount: null,
  max_amount: null,
  risk_profile: 'medium',
  commission_percent: null,
  commission_fixed: null,
});

const filters = ref<Filters>({
  payment_methods: [],
  min_rating: null,
  min_trades: null,
  min_amount: null,
  max_amount: null,
});

const saving = ref(false);
const savingFilters = ref(false);

async function saveProfile() {
  saving.value = true;
  try {
    // TODO: API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    $q.notify({
      type: 'positive',
      message: 'Профиль сохранён',
    });
  } finally {
    saving.value = false;
  }
}

async function saveFilters() {
  savingFilters.value = true;
  try {
    // TODO: API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    $q.notify({
      type: 'positive',
      message: 'Фильтры сохранены',
    });
  } finally {
    savingFilters.value = false;
  }
}

onMounted(async () => {
  // TODO: Load profile and filters from API
});
</script>
