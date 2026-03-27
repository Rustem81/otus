<template>
  <q-page class="flex flex-center">
    <q-card class="login-card q-pa-lg">
      <q-card-section>
        <div class="text-h5 text-center q-mb-md">MEXC P2P Aggregator</div>
        <div class="text-subtitle2 text-center text-grey q-mb-lg">
          Вход в систему
        </div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="onSubmit" class="q-gutter-md">
          <q-input
            v-model="email"
            label="Email"
            type="email"
            outlined
            :rules="[(val) => !!val || 'Обязательное поле']"
          />

          <q-input
            v-model="password"
            label="Пароль"
            type="password"
            outlined
            :rules="passwordRules"
          />

          <q-banner v-if="authStore.error" class="bg-negative text-white q-mb-md">
            {{ authStore.error }}
          </q-banner>

          <q-btn
            type="submit"
            color="primary"
            class="full-width"
            :loading="authStore.isLoading"
            :label="isLogin ? 'Войти' : 'Зарегистрироваться'"
          />

          <q-btn
            flat
            color="primary"
            class="full-width"
            :label="isLogin ? 'Создать аккаунт' : 'Уже есть аккаунт'"
            @click="isLogin = !isLogin"
          />
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const isLogin = ref(true);

const passwordRules = [
  (val: string) => !!val || 'Обязательное поле',
  (val: string) => val.length >= 8 || 'Минимум 8 символов',
];

async function onSubmit() {
  let success;
  if (isLogin.value) {
    success = await authStore.login({
      email: email.value,
      password: password.value,
    });
  } else {
    success = await authStore.register({
      email: email.value,
      password: password.value,
    });
  }

  if (success) {
    router.push('/');
  }
}
</script>

<style scoped>
.login-card {
  width: 100%;
  max-width: 400px;
}
</style>
