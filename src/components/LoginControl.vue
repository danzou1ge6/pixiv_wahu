<template>
  <transition appear enter-active-class="animated fadeInDown" leave-active-class="animated fadeOutUp">

    <q-card class="login-ctl-box" v-if="props.modelValue">

      <q-card-section v-if="accountSession !== null && accountSession != undefined">
        <div class="text-h6">{{ accountSession.user_name }}</div>
        <div class="text-body-1 text-grey-8">
          / uid = {{ accountSession.user_id }}
        </div>
        <div class="text-body-1 text-grey-8">
          将于 {{ accountSession.expire_at }} 过期
        </div>
      </q-card-section>

      <q-card-actions v-if="accountSession === null">
        <div class="text-subtitle-2 text-grey-8">无 Access Token ，无法使用 PixivAPI</div>
        <q-btn @click="attemptLogin" flat stretch :loading="loginLoading">
          获取 Access Token
          <q-tooltip>
            需要提供 Refresh Token
          </q-tooltip>
        </q-btn>
      </q-card-actions>

    </q-card>
  </transition>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import * as wm from '../plugins/wahuBridge/methods'
import type { AccountSession } from 'src/plugins/wahuBridge/methods';

const loginLoading = ref<boolean>(false)

const props = defineProps<{
  modelValue: boolean
}>()

const accountSession = ref<AccountSession | null>()

function updateAS() {
  wm.p_account_session()
    .then(as => { accountSession.value = as })
}

onMounted(updateAS)

watch(props, () => {
  if (props.modelValue) { updateAS() }
})

function attemptLogin() {
  loginLoading.value = true
  wm.p_attempt_login()
    .then(ac => {
      accountSession.value = ac
      loginLoading.value = false
    })
}

const emits = defineEmits<{
  (e: 'update:modelValue', id: boolean): void
}>()

</script>

<style scoped>
.login-ctl-box {
  position: fixed;
  width: 300px;
  right: 10px;
  top: 55px;
  z-index: 999;
}
</style>
