/**
 * 线索 Store 缓存策略测试
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useXiansuoStore } from '@/stores/modules/xiansuo'
import {
  xiansuoApi,
  xiansuoLaiyuanApi,
  xiansuoZhuangtaiApi,
  xiansuoGenjinApi
} from '@/api/modules/xiansuo'

vi.mock('@/api/modules/xiansuo', () => ({
  xiansuoApi: {
    getList: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    updateStatus: vi.fn(),
    assign: vi.fn(),
    getDetail: vi.fn(),
    getStatistics: vi.fn()
  },
  xiansuoLaiyuanApi: {
    getList: vi.fn(),
    getActiveList: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getDetail: vi.fn()
  },
  xiansuoZhuangtaiApi: {
    getList: vi.fn(),
    getActiveList: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getDetail: vi.fn()
  },
  xiansuoGenjinApi: {
    getList: vi.fn(),
    getByXiansuo: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getDetail: vi.fn()
  }
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  }
}))

describe('Xiansuo Store 缓存逻辑', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('首次拉取时应调用接口并写入缓存，重复查询命中缓存', async () => {
    const store = useXiansuoStore()
    const response = {
      items: [
        {
          id: '1',
          xiansuo_bianma: 'XS20240101001',
          gongsi_mingcheng: '测试公司',
          lianxi_ren: '联系人',
          zhiliang_pinggu: 'high',
          zhiliang_fenshu: 90,
          laiyuan_id: 'source-1',
          xiansuo_zhuangtai: 'new',
          genjin_cishu: 0,
          shi_zhuanhua: 'N',
          zhuanhua_jine: 0,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ],
      total: 1,
      page: 1,
      size: 20
    }

    vi.mocked(xiansuoApi.getList).mockResolvedValue(response)

    await store.fetchXiansuoList({ page: 1, size: 20 })
    expect(xiansuoApi.getList).toHaveBeenCalledTimes(1)
    expect(store.xiansuo_list).toHaveLength(1)

    vi.mocked(xiansuoApi.getList).mockClear()
    await store.fetchXiansuoList({ page: 1, size: 20 })
    expect(xiansuoApi.getList).not.toHaveBeenCalled()
  })

  it('强制刷新应忽略缓存并重新请求', async () => {
    const store = useXiansuoStore()
    const response = {
      items: [],
      total: 0,
      page: 1,
      size: 20
    }

    vi.mocked(xiansuoApi.getList).mockResolvedValue(response)

    await store.fetchXiansuoList({ page: 1, size: 20 })
    expect(xiansuoApi.getList).toHaveBeenCalledTimes(1)

    await store.fetchXiansuoList({ page: 1, size: 20 }, true)
    expect(xiansuoApi.getList).toHaveBeenCalledTimes(2)
  })

  it('线索来源缓存未过期时应避免重复请求', async () => {
    const store = useXiansuoStore()
    const activeList = [
      {
        id: 'source-1',
        laiyuan_mingcheng: '渠道 A',
        laiyuan_bianma: 'qa',
        laiyuan_leixing: 'online',
        huoqu_chengben: 0,
        xiansuo_shuliang: 0,
        zhuanhua_shuliang: 0,
        zhuanhua_lv: 0,
        zhuangtai: 'active',
        paixu: 1,
        miaoshu: '测试',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    ]

    vi.mocked(xiansuoLaiyuanApi.getActiveList).mockResolvedValue(activeList)

    await store.fetchActiveLaiyuanList()
    expect(xiansuoLaiyuanApi.getActiveList).toHaveBeenCalledTimes(1)

    vi.mocked(xiansuoLaiyuanApi.getActiveList).mockClear()
    store.cache.laiyuan_loaded = true
    store.cache.laiyuan_timestamp = Date.now()

    await store.fetchActiveLaiyuanList()
    expect(xiansuoLaiyuanApi.getActiveList).not.toHaveBeenCalled()
  })
})
