
import request from '@/axios';
import { baseUrl } from '@/config/env';
export const list = (data) => {
  return request({
    url: baseUrl + '/crud/list',
    method: 'get',
    meta: {
      isSerialize: true
    },
    params: data
  })
}
export const del = (id) => request.delete(baseUrl + '/crud', {
  params: {
    id
  }
})
export const add = (data) => request({
  url: baseUrl + '/crud',
  method: 'post',
  meta: {
    isSerialize: true
  },
  data: data
})
export const update = (id, data) => request({
  url: baseUrl + '/crud',
  method: 'put',
  meta: {
    isSerialize: true
  },
  data: data
})



