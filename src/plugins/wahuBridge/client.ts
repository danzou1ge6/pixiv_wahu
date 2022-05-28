import { isBuiltInDirective } from '@vue/shared';
import { ref } from 'vue';
import { wsRPCURL } from '../../constants'
import { pushNoti } from '../notifications'

/**
 * Post 接口
 */

interface PostRPCReturn<T> {
    type: 'normal' | 'generator';
    return: T | string
}


async function wahuPostRPCCall<T>(method: string, args: object)
    : Promise<T | AsyncIterable<T>> {
    /*
    使用 RPC 调用 WahuMethod
    如果后端返回的 `RPCReturn.type` 为 `normal` ，则返回 `RPCReturn.return` ，
    如果为 `generator` ，则返回一个异步生成器
    */
    let resp = await fetch('/rpc', {
        method: 'POST',
        body: JSON.stringify({
            method: method,
            args: args
        })
    })

    if (!resp.ok) {
        pushNoti({
            level: 'error',
            msg: '服务器响应 Not OK . 状态码 ' + resp.status
        })
        throw Error('服务器响应 not ok')
    }

    let ret = await resp.json() as PostRPCReturn<T>

    if (ret.type == 'normal') {

        return (<T>ret.return)
    } else if (ret.type == 'generator') {

        let gkey = ret.return as string

        async function* g(): AsyncIterable<T> {
            while (true) {
                let ret = await wahuRPCCall<T>('wahu_anext', { key: gkey })
                if (ret === undefined) { break }
                yield ret as T
            }
        }

        return g()
    } else {
        throw TypeError(`不合法的返回类型 ${ret.type}`)
    }
}

/*
 *  WebSocket 接口
 */

class WahuStopIteration {
    constructor() { }
}

interface WsRPCReturn<T> {
    type: 'normal' | 'generator' | 'exception' | 'dl_progress' | 'warning';
    return: T | string;
    mcid: number
}

let socket: WebSocket

let socketOpenPromise: Promise<undefined>

const soecketStatusReact = ref<number>(WebSocket.CLOSED)

interface PromiseCbkPool {
    [index: number]: [Function, Function]
}

const promiseCbkPool: PromiseCbkPool = {}

function randomID(): number {
    let ret
    do {
        ret = Math.floor(Math.random() * 100000000)
    } while (promiseCbkPool[ret] !== undefined)

    return ret
}

let dlProgressReportCbk: Function = (ret: any) => { }

function handleSoecketMessage(ev: MessageEvent) {

    const ret = JSON.parse(ev.data) as WsRPCReturn<any>

    if (promiseCbkPool[ret.mcid] !== undefined) {

        const [resolve, reject] = promiseCbkPool[ret.mcid]

        if (ret.type == 'normal') {

            resolve(ret.return)

        } else if (ret.type == 'generator') {

            const gkey = ret.return as string

            async function* g(): AsyncGenerator<any, any, any> {
                let sendVal = null

                while (true) {
                    const ret: any = await wahuRPCCall<any>(
                        'wahu_anext',
                        { key: gkey, send_val: sendVal }
                    )
                    if (ret === null) { break }

                    try {
                        sendVal = yield ret as any

                        if(sendVal === undefined) {
                            sendVal = null
                        }

                    } catch (e) {
                        if (e instanceof WahuStopIteration) {
                            wahuRPCCall('wahu_dispose_generator', { key: gkey })
                            return
                        }
                    }
                }
            }

            resolve(g())

        } else if (ret.type == 'exception') {
            pushNoti({
                level: 'error',
                msg: '异常：' + ret.return
            })
            reject(ret.return)

        } else {
            reject()
            throw TypeError('不合法的返回类型 ' + ret.type)
        }

    } else {

        if (ret.type == 'warning') {
            pushNoti({
                level: 'warning',
                msg: ret.return
            })

        } else if (ret.type == 'dl_progress') {

            dlProgressReportCbk(ret.return)

        } else {
            throw TypeError(`不合法的返回类型 ${ret.type}`)
        }
    }
}


async function wahuRPCCall<T>(method: string, args: object)
    : Promise<T | AsyncIterable<T>> {

    await socketOpenPromise

    const mcid = randomID()

    const p = new Promise<T | AsyncIterable<T>>((resolve, reject) => {
        promiseCbkPool[mcid] = [resolve, reject]
    })

    socket.send(JSON.stringify({
        method: method,
        args: args,
        mcid: mcid
    }))


    return p
}

function initWahuWsBridge(): void {
    pushNoti({ level: 'info', msg: '尝试连接 WebSocket RPC' })
    socket = new WebSocket(`ws://${location.host}${wsRPCURL}`)

    socketOpenPromise = new Promise((resolve) => {

        socket.addEventListener('open', () => {
            pushNoti({ level: 'success', msg: 'WebSocket RPC 连接成功' })

            soecketStatusReact.value = WebSocket.OPEN

            socket.addEventListener('message', handleSoecketMessage)

            socket.addEventListener('close', () => {
                pushNoti({ level: 'warning', msg: 'WebSocket RPC 连接关闭' })
                initWahuWsBridge()
                soecketStatusReact.value = WebSocket.CLOSED
            })

            socket.addEventListener('error', () => {
                pushNoti({ level: 'error', msg: 'WebSocket RPC 连接出错' })
                soecketStatusReact.value = WebSocket.CLOSED
            })

            resolve(undefined)
        })
    })

    setTimeout(() => {
        if (socket.readyState != socket.OPEN) {
            initWahuWsBridge()
        }
    }, 5000)
}

function regDlProgressReportCbk(f: Function) {
    dlProgressReportCbk = f
}



export { wahuRPCCall, initWahuWsBridge, regDlProgressReportCbk, WahuStopIteration, soecketStatusReact }
