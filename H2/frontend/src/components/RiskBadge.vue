<template>
  <q-badge
    :color="badgeColor"
    :label="label"
    class="cursor-pointer"
  >
    <q-tooltip v-if="explanation">
      {{ explanation }}
    </q-tooltip>
  </q-badge>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  score: number;
  category: string;
  explanation?: string;
}>();

const badgeColor = computed(() => {
  switch (props.category) {
    case 'low':
      return 'positive';
    case 'medium':
      return 'warning';
    case 'high':
      return 'negative';
    default:
      return 'grey';
  }
});

const label = computed(() => `${props.score}/10`);
</script>
