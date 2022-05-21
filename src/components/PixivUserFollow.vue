<template>
  <q-btn @click="handleFollow(!modelValue)" flat :loading="followLoading">
    {{ modelValue ? '取消关注' : '关注' }}</q-btn>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { pushNoti } from 'src/plugins/notifications';
import * as wm from '../plugins/wahuBridge/methods'

const props = defineProps<{
  uid: number, name: string
  modelValue: boolean
}>()
const emits = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
}>()


const followLoading = ref<boolean>(false)

function handleFollow(val: boolean) {
  if (val) {
    if (props.modelValue) {
      pushNoti(
        { level: 'warning', msg: '已经关注用户 ' + props.name + ' ，无法关注' })
      return
    }
    followLoading.value = true
    wm.p_user_follow_add(props.uid)
      .then(() => {
        pushNoti({ level: 'success', msg: '关注了用户 ' + props.name })
        emits('update:modelValue', true)
        followLoading.value = false
      })
  } else {
    if (!props.modelValue) {
      pushNoti({ level: 'warning', msg: '未关注用户 ' + props.name + ' ，不能取消关注' })
      return
    }
    followLoading.value = true
    wm.p_user_follow_rm(props.uid)
      .then(() => {
        pushNoti({ level: 'success', msg: '取消关注了用户 ' + props.name })
        emits('update:modelValue', false)
        followLoading.value = false
      })
  }

}
</script>
