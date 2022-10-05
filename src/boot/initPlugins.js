import { boot } from 'quasar/wrappers'
import { initWahuWsBridge } from '../plugins/wahuBridge/client'
import { initNotifications } from '../plugins/notifications'
// "async" is optional;
// more info on params: https://v2.quasar.dev/quasar-cli/boot-files
export default boot(({ app }) => {

  app.use(initWahuWsBridge)
  app.use(initNotifications)
})
