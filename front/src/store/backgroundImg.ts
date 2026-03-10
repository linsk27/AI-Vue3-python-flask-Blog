import { defineStore } from 'pinia'
import piniaPersistConfig from './config/piniaPersist'
interface IImg {
    url: string
    ifShowStar: boolean
}
export const useImgStore = defineStore('ImgStore', {
    state: (): IImg => ({
        url: '',
        ifShowStar: false
    }),
    actions: {
        changeUrl(newUrl: string) {
            this.url = newUrl
        },
        toggleStar() {
            this.ifShowStar = !this.ifShowStar
        }
    },
    persist: piniaPersistConfig('ImgStore')
})
