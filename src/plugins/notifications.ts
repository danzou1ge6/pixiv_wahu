import { ref } from "vue"
import { onSocketOpen } from "./wahuBridge/client"
import { wahu_logger_client } from './wahuBridge/methods'

interface AppNotification {
    level: 'error' | 'warning' | 'info' | 'success'
    msg: string
}

export type { AppNotification }


const appAllNoti = ref<Array<AppNotification>>([])

export function pushNoti(noti: AppNotification) : void {
    appAllNoti.value.push(noti)
}


async function listenLogGen(gen: AsyncGenerator<[number, string], undefined, null>) {
  while(true) {
    const ret = await gen.next()

    if(ret.value === undefined) {
      throw(new Error('logGen returned undefined'))
    }

    const [level, msg] = ret.value

    if(level == 30) { // warning
      pushNoti({level: 'warning', msg})
    }else if(level >= 40) {  // error, fatal
      pushNoti({level: 'error', msg})
    }
  }
}

function initNotifications() {
    onSocketOpen(() => {
        console.log('Getting logger client')
        wahu_logger_client()
            .then(logGen => {
            listenLogGen(logGen)
            })
        }
    )
}


export { appAllNoti, initNotifications }
