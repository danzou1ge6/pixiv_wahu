<template>
    <q-img :src="homeImageURL" v-show="showKud" autofocus ref="image" fit="cover"
      class="animated fadeInDown bg-img">

      <Transition appear enter-active-class="animated fadeInLeft" leave-active-class="animated fadeOutLeft">
          <WahuCli :dark="true" width="75vw" height="100%" v-show="showCli"></WahuCli>
      </Transition>

      <div class="text-body-2 absolute-top-right animated fadeInUp" v-show="showWahu">クドリャフカ - 73072668 by クー </div>
    </q-img>

</template>

<script setup lang="ts">
import { homeImageURL } from 'src/constants';
import WahuCli from 'src/components/WahuCli.vue';
import { onMounted, ref } from 'vue';

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

<style scoped>
.bg-img {
  position: fixed;
  left: 0px;
  top: 50px;
  widows: 100%;
  height: calc(100vh - 50px);
}
</style>
