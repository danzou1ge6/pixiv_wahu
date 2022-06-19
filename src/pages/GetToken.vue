<template>
  <div class="q-ma-md">
    <q-stepper v-model="stepN" vertical color="primary" animated>
      <q-step :name="1" title="准备" :done="stepN > 1" icon="assignment">
        <div>Pixiv 使用 refresh_token 进行身份验证</div>
        <div>为了获得 refresh_token ，需要以下准备</div>
        <ul>
          <li>有一个现代浏览器，如 Edge, Chrome, Firefox</li>
          <li>打开浏览器的「开发者工具」；有的「开发者工具」界面为英文，下述皆为中文，请自行辨认对应英文</li>
          <li>能够访问 Pixiv</li>
        </ul>
        <q-stepper-navigation>
          <q-btn @click="stepN = 2" color="primary" label="继续"></q-btn>
        </q-stepper-navigation>
      </q-step>

      <q-step :name="2" title="前往登录页面" :done="stepN > 2" icon="launch">
        <q-btn @click="openPixivLogin">使用此按钮打开 Pixiv 登录页面</q-btn>
        <div class="q-mt-sm">打开后请回到此页面，继续下面的步骤</div>
        <q-stepper-navigation>
          <q-btn @click="stepN = 3" color="primary" label="继续"></q-btn>
          <q-btn flat @click="stepN = 1" color="primary" label="返回"></q-btn>
        </q-stepper-navigation>
      </q-step>

      <q-step :name="3" title="获得 code" :done="stepN > 3" icon="code">
        <div>接下来的操作需要用到浏览器的「开发者工具 / DevTools」</div>
        <ul>
          <li>在刚才打开的 Pixiv 登陆页面打开「开发者工具」</li>
          <li>将「开发者工具」切换到「网络 / Network」 标签栏</li>
          <li>开启「持续记录 / 保留日志」. 如果不开启，下面所需要的字段可能在跳转后丢失</li>
          <li>在「开发者工具」的「筛选 / Filter」框中输入「callback?」</li>
          <li>登陆账号. 登录过程中产生的请求会被「开发者工具」记录</li>
          <li>
            登陆成功后，「开发者工具」的「网络」页面会出现一个形如
            "https://app-api.pixiv.net/.../callback?state=...&code=..."的字段
          </li>
          <li>将「code=」后的内容复制到下面的输入框中，点击提交</li>
        </ul>
        <q-input v-model="code" label="Code" @keyup.enter="submit"></q-input>
        <q-stepper-navigation>
          <q-btn @click="submit" color="primary" label="提交"></q-btn>
          <q-btn flat @click="stepN = 2" color="primary" label="返回"></q-btn>
        </q-stepper-navigation>
      </q-step>

      <q-step :name="4" title="完成" icon="check">
        <div>Refresh Token 为</div>
        <div class="text-h5">{{ refreshToken }}</div>
        <div>此字符串可以用于无密码登录 Pixiv 账号，请妥善保管</div>
        <div v-if="rtPath === null">
          目前未设定 refresh_token_path ，即保存 refresh_token 的文件路径.
          请设定此配置项后将上述 refresh_token 复制到该文件中.
        </div>
        <div v-else>已保存至 {{ rtPath }}</div>
      </q-step>

    </q-stepper>
  </div>
</template>

<script setup lang="ts">

import { onMounted, ref } from 'vue'
import { token_get_loginurl, token_submit_code, get_config } from 'src/plugins/wahuBridge/methods';

const emits = defineEmits<{
  (e: 'updateProps', val: object): void,
  (e: 'updateTitle', val: string): void,
}>()

onMounted(() => {
  emits('updateTitle', '获取 RefreshToken')
})

const stepN = ref<number>(1)
const code = ref<string>('')
const refreshToken = ref<string>()

const rtPath = ref<string | null>()
onMounted(() => {
  get_config('refresh_token_path')
    .then(p => { rtPath.value = p })
})

function openPixivLogin() {
  token_get_loginurl()
    .then(url => { window.open(url) })
}

function submit() {
  token_submit_code(code.value)
    .then(rt => {
      refreshToken.value = rt
      stepN.value = 4
    })
}

</script>

