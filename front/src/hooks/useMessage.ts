/*
 * @Author: 叶剑鑫 yejianxin2022@dingtalk.com
 * @Date: 2025-04-03 16:14:30
 * @LastEditTime: 2025-04-03 16:14:30
 * @Description: 消息提示 hook
 * @Changelog:
 */

import { ElMessage } from 'element-plus'

export const useElMessage = () => {
    const message = {
        success: (message: string): void => {
            ElMessage({
                message,
                type: 'success',
                duration: 600
            })
        },
        warning: (message: string): void => {
            ElMessage({
                message,
                type: 'warning',
                duration: 1000
            })
        },
        info: (message: string): void => {
            ElMessage({
                message,
                type: 'info',
                duration: 1000
            })
        },
        error: (message: string): void => {
            ElMessage({
                message,
                type: 'error',
                duration: 1000
            })
        }
    }

    return {
        message
    }
}
