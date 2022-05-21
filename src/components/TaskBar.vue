<template>
  <div style="max-width: 80vw">
    <q-tabs v-model="selected" outside-arrowsalign="right">
      <transition-group appear enter-active-class="animated fadeInDown" leave-active-class="animated fadeInUp">
        <div v-for="(win, i) in tabbedWindows" :key="win.key">
          <q-tab no-caps :name="i" @click="displayedWindowN = i">
            <div class="row">
              <div class="col-10" style="max-width: 180px;overflow: hidden; text-overflow: clip;">
                {{ win.title }}
              </div>
              <div class="col">
                <q-btn size="10px" padding="none" @click="removeWindow(i)" flat>
                  <q-icon name="clear"></q-icon>
                </q-btn>
              </div>
            </div>
          </q-tab>
        </div>
      </transition-group>

      <q-btn-dropdown auto-close stretch flat v-show="openedWindows.length > maxTabbedN">
        <q-list>
          <q-item v-for="(win, j) in groupedWindows" :key="j + maxTabbedN" clickable
            @click="displayedWindowN = j + maxTabbedN">
            <div>{{ win.title }}</div>
            <q-item-section side>
              <q-btn size="10px" padding="none" @click="removeWindow(j + maxTabbedN)" flat class="float-right">
                <q-icon name="clear"></q-icon>
              </q-btn>
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </q-tabs>
  </div>
</template>

<script setup lang="ts">
import { computed } from '@vue/reactivity';
import { ref, watch } from 'vue';
import { openedWindows, displayedWindowN, removeWindow } from '../plugins/windowManager';
import { useQuasar } from 'quasar';

const selected = ref<number>(0)

watch(displayedWindowN, () => {
  selected.value = displayedWindowN.value
})

const $q = useQuasar()

const maxTabbedN = computed(() => {
  return Math.floor($q.screen.width * 0.9 / 180)
})

const tabbedWindows = computed(() => {
  if (openedWindows.value.length >= maxTabbedN.value) {
    return openedWindows.value.slice(0, maxTabbedN.value)
  } else {
    return openedWindows.value
  }
})

const groupedWindows = computed(() => {
  if (openedWindows.value.length >= maxTabbedN.value) {
    return openedWindows.value.slice(maxTabbedN.value)
  } else {
    return []
  }
})
</script>

