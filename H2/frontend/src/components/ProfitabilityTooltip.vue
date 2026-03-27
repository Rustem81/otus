<template>
  <span :class="profitClass">
    {{ formattedValue }}
    <q-tooltip>
      <div class="text-caption">
        <div>Чистая доходность:</div>
        <div class="text-weight-bold">{{ formattedValue }}</div>
        <div v-if="value > 0" class="text-positive">Профит</div>
        <div v-else-if="value < 0" class="text-negative">Убыток</div>
        <div v-else>Без изменений</div>
      </div>
    </q-tooltip>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  value: number;
}>();

const formattedValue = computed(() => {
  const sign = props.value > 0 ? '+' : '';
  return `${sign}${props.value.toFixed(2)}%`;
});

const profitClass = computed(() => {
  if (props.value > 0) return 'text-positive';
  if (props.value < 0) return 'text-negative';
  return 'text-grey';
});
</script>
