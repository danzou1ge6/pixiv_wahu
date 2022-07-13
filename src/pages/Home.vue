<template>

  <div class="container">
    <WahuCli v-show="showCli" class="wahu-cli"></WahuCli>

  </div>


</template>

<script setup lang="ts">
import WahuCli from 'src/components/WahuCli.vue';
import { computed, onMounted, ref } from 'vue';
import { useQuasar } from 'quasar';

const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()
onMounted(() => {
  emits('updateTitle', 'Home')
})

const showWahu = ref<boolean>(false)
const showKud = ref<boolean>(false)

const showCli = ref<boolean>(false)

const image = ref<HTMLTemplateElement | null>(null)

const $q = useQuasar()

const terminalWidth = computed(() => {
  if($q.platform.is.mobile) {
    return '95vw'
  }else {
    return '75vw'
  }
})

onMounted(() => {
  setTimeout(() => {
    showWahu.value = true
  }, 500)
  setTimeout(() => {
    showKud.value = true
    showCli.value = true
  }, 250)

})
</script>

<style scoped lang="scss">
.container {
  position: absolute;
  left: 0px;
  top: 0px;
  height: $page-height;
  width: 100vw;
}

.wahu-cli {
  width: 100%;
  height: 100%;
}
</style>
