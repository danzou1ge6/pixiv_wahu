<template>
  <q-input @focusout="update" v-model="input" :rules="[validateArrayOfNumber]" hint="用英文逗号「,」分开" hide-hint>
  </q-input>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

const props = defineProps<{
  modelValue: Array<number>
}>()
const emits = defineEmits<{
  (e: 'update:modelValue', val: Array<number>): void
}>()


function validateArrayOfNumber(val: string): boolean {
  const ls = val.split(',')

  for (const item of ls) {
    if (isNaN(Number(item))) {
      return false
    }
  }
  return true
}

const input = ref<string>(props.modelValue.join(','))

function update() {
  let ret = []
  for (let s of input.value.split(',')) {
    if (s !== '') { ret.push(Number(s)) }
  }
  console.log(input.value, ret)
  emits('update:modelValue', ret)
}

</script>
