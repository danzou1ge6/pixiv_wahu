<template>
  <slot :set-hover="setHover" :unset-hover="unsetHover" :hover-id="hoverId"></slot>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const hoverId = ref<any>()

function setHover(id: any) { hoverId.value = id }
function unsetHover() { hoverId.value = undefined }
</script>

