import { isBuiltInDirective } from '@vue/shared';
import { ref } from 'vue';
import { wsRPCURL } from '../../constants'
import { pushNoti } from '../notifications'

/**
 * Post 接口
 */

interface PostRPCReturn<T> {
    type: 'normal' | 'generator';
    return: T | string | Array<string>
}

function wahuPostRPCGeneratorFactory<T>(gkey: string) {

    async function* g(): AsyncIterable<T> {
        while (true) {
            let ret = await wahuPostRPCCall<T>('wahu_anext', [ gkey ])
            if (ret === undefined) { break }
            yield ret as T
        }
    }

    return g()

}


async function wahuPostRPCCall<T>(method: string, args: Array<any>)
    : Promise<T | AsyncIterable<T> | Array<AsyncIterable<T>>> {
    /*
    使用 RPC 调用 WahuMethod
    如果后端返回的 `RPCReturn.type` 为 `normal` ，则返回 `RPCReturn.return` ，
    如果为 `generator` ，则返回一个或若干个异步生成器
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

        if(typeof(ret.return) == 'object') {
            let gkeys = ret.return as Array<string>

            return gkeys.map(gkey => wahuPostRPCGeneratorFactory(gkey))
        }else {

            let gkey = ret.return as string

            return wahuPostRPCGeneratorFactory(gkey)
        }

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

class WahuBackendException {
    type: string
    repr: string
    constructor(type: string, repr: string) {
        this.type = type
        this.repr = repr
    }
}

interface WsRPCReturn<T> {
    type: 'normal' | 'generator' | 'error' | 'dl_progress' | 'warning' | 'failure';
    return: T | string | Array<string>;
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

function wahuWsRPCGeneratorFactory(gkey: string) {

    async function* g(): AsyncGenerator<any, any, any> {
        let sendVal = null

        while (true) {
            const ret: any = await wahuRPCCall<any>(
                'wahu_anext',
                [ gkey, sendVal ]
            )
            if (ret === null) { break }

            try {
                sendVal = yield ret as any

                if(sendVal === undefined) {
                    sendVal = null
                }

            } catch (e) {
                if (e instanceof WahuStopIteration) {
                    wahuRPCCall('wahu_dispose_generator', [ gkey, ])
                    return
                }
            }
        }
    }
    return g()
}

function handleSoecketMessage(ev: MessageEvent) {

    const ret = JSON.parse(ev.data) as WsRPCReturn<any>

    if (promiseCbkPool[ret.mcid] !== undefined) {

        const [resolve, reject] = promiseCbkPool[ret.mcid]

        if (ret.type == 'normal') {

            resolve(ret.return)

        } else if (ret.type == 'generator') {

            if(typeof(ret.return) == 'object') {
                const gkeys = ret.return as Array<string>

                resolve(gkeys.map(gkey=> wahuWsRPCGeneratorFactory(gkey)))

            }else {
                const gkey = ret.return as string

                resolve(wahuWsRPCGeneratorFactory(gkey))
            }

        } else if (ret.type == 'failure') {
            const [type, repr] = ret.return
            reject(new WahuBackendException(type, repr))

        } else {
            reject()
            throw TypeError('不合法的返回类型 ' + ret.type)
        }

    } else {

            throw TypeError(`不合法的返回类型 ${ret.type}`)
    }
}


async function wahuRPCCall<T>(method: string, args: Array<any>)
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

let onOpenHooks: Array<()=>void> = []

function initWahuWsBridge(): void {
    pushNoti({ level: 'info', msg: '尝试连接 WebSocket RPC' })
    socket = new WebSocket(`ws://${location.host}${wsRPCURL}`)

    socketOpenPromise = new Promise((resolve) => {

        socket.addEventListener('open', () => {
            pushNoti({ level: 'success', msg: 'WebSocket RPC 连接成功' })

            soecketStatusReact.value = WebSocket.OPEN

            socket.addEventListener('message', handleSoecketMessage)

            for(const hook of onOpenHooks) {
                hook()
            }

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

}

function onSocketOpen(hook: ()=>void) : (()=>void) | undefined {
    for(const h of onOpenHooks) {
        if(h == hook) {
            return undefined
        }
    }
    onOpenHooks.push(hook)
    return () => {
        onOpenHooks.forEach((h, idx) => {
            if(h == hook) {
                onOpenHooks.splice(idx, 1)
            }
        })
    }
}


export { wahuRPCCall, initWahuWsBridge, WahuStopIteration,
    soecketStatusReact, WahuBackendException, onSocketOpen, onOpenHooks }
