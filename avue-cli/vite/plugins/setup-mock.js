import { viteMockServe } from "vite-plugin-mock";
export default function createSetupMock () {
  return viteMockServe({// 更多配置见最下方
    mockPath: "./mock/", //mock文件地址 
    injectCode: ` import { setupProdMockServer } from './mockProdServer'; setupProdMockServer(); `,
    logger: false, //是否在控制台显示请求日志 
    supportTs: false //打开后，可以读取 ts 文件模块。 请注意，打开后将无法监视.js 文件 
  })
}
