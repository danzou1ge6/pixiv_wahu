<template>
  <slot :getState="getState" :toggle="toggle"></slot>
</template>

<script setup lang="ts">

const props = defineProps<{ modelValue: Array<number> }>()
const emits = defineEmits<{ (e: 'update:modelValue', v: Array<number>): void }>()


function getState(id: number) {
  if (props.modelValue.indexOf(id) != -1) {
    return true
  } else { return false }
}

function toggle(id: number, state: boolean) {
  const idx = props.modelValue.indexOf(id)
  if (state) {
    if (idx == -1) {
      emits('update:modelValue', [id].concat(props.modelValue))
    }
  } else {
    if (idx != -1) {
      emits('update:modelValue', props.modelValue.slice(0, idx).concat(props.modelValue.slice(idx + 1)))
    }
  }
}
</script>
