import { ref } from "vue"

interface AppNotification {
    level: 'error' | 'warning' | 'info' | 'success'
    msg: string
}

export type { AppNotification }


const appAllNoti = ref<Array<AppNotification>>([])

export function pushNoti(noti: AppNotification) : void {
    appAllNoti.value.push(noti)
}



export { appAllNoti }
