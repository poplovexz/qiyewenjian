/**
 * 财务设置API
 */
import request from '@/utils/request'

// 通用列表参数类型
interface ListParams {
  page?: number
  size?: number
  zhuangtai?: string
  [key: string]: string | number | undefined
}

// ==================== 收付款渠道 ====================
export interface ShoufukuanQudao {
  id?: string
  mingcheng: string
  leixing: string
  zhanghu_mingcheng?: string
  zhanghu_haoma?: string
  kaihuhang?: string
  lianhanghao?: string
  miaoshu?: string
  paixu?: number
  zhuangtai?: string
  created_at?: string
  updated_at?: string
}

export function getQudaoList(params?: ListParams) {
  return request({
    url: '/finance-settings/qudao',
    method: 'get',
    params
  })
}

export function getQudaoDetail(id: string) {
  return request({
    url: `/finance-settings/qudao/${id}`,
    method: 'get'
  })
}

export function createQudao(data: ShoufukuanQudao) {
  return request({
    url: '/finance-settings/qudao',
    method: 'post',
    data
  })
}

export function updateQudao(id: string, data: Partial<ShoufukuanQudao>) {
  return request({
    url: `/finance-settings/qudao/${id}`,
    method: 'put',
    data
  })
}

export function deleteQudao(id: string) {
  return request({
    url: `/finance-settings/qudao/${id}`,
    method: 'delete'
  })
}

// ==================== 收入类别 ====================
export interface ShouruLeibie {
  id?: string
  mingcheng: string
  bianma?: string
  miaoshu?: string
  paixu?: number
  zhuangtai?: string
  created_at?: string
  updated_at?: string
}

export function getShouruLeibieList(params?: ListParams) {
  return request({
    url: '/finance-settings/shouru-leibie',
    method: 'get',
    params
  })
}

export function createShouruLeibie(data: ShouruLeibie) {
  return request({
    url: '/finance-settings/shouru-leibie',
    method: 'post',
    data
  })
}

export function updateShouruLeibie(id: string, data: Partial<ShouruLeibie>) {
  return request({
    url: `/finance-settings/shouru-leibie/${id}`,
    method: 'put',
    data
  })
}

export function deleteShouruLeibie(id: string) {
  return request({
    url: `/finance-settings/shouru-leibie/${id}`,
    method: 'delete'
  })
}

// ==================== 报销类别 ====================
export interface BaoxiaoLeibie {
  id?: string
  mingcheng: string
  bianma?: string
  miaoshu?: string
  paixu?: number
  zhuangtai?: string
  created_at?: string
  updated_at?: string
}

export function getBaoxiaoLeibieList(params?: ListParams) {
  return request({
    url: '/finance-settings/baoxiao-leibie',
    method: 'get',
    params
  })
}

export function createBaoxiaoLeibie(data: BaoxiaoLeibie) {
  return request({
    url: '/finance-settings/baoxiao-leibie',
    method: 'post',
    data
  })
}

export function updateBaoxiaoLeibie(id: string, data: Partial<BaoxiaoLeibie>) {
  return request({
    url: `/finance-settings/baoxiao-leibie/${id}`,
    method: 'put',
    data
  })
}

export function deleteBaoxiaoLeibie(id: string) {
  return request({
    url: `/finance-settings/baoxiao-leibie/${id}`,
    method: 'delete'
  })
}

// ==================== 支出类别 ====================
export interface ZhichuLeibie {
  id?: string
  mingcheng: string
  bianma?: string
  fenlei?: string
  miaoshu?: string
  paixu?: number
  zhuangtai?: string
  created_at?: string
  updated_at?: string
}

export function getZhichuLeibieList(params?: ListParams) {
  return request({
    url: '/finance-settings/zhichu-leibie',
    method: 'get',
    params
  })
}

export function createZhichuLeibie(data: ZhichuLeibie) {
  return request({
    url: '/finance-settings/zhichu-leibie',
    method: 'post',
    data
  })
}

export function updateZhichuLeibie(id: string, data: Partial<ZhichuLeibie>) {
  return request({
    url: `/finance-settings/zhichu-leibie/${id}`,
    method: 'put',
    data
  })
}

export function deleteZhichuLeibie(id: string) {
  return request({
    url: `/finance-settings/zhichu-leibie/${id}`,
    method: 'delete'
  })
}
