/**
 * 线索管理相关类型定义
 */

// 线索来源
export interface XiansuoLaiyuan {
  id: string
  laiyuan_mingcheng: string
  laiyuan_bianma: string
  laiyuan_leixing: string
  huoqu_chengben: number
  xiansuo_shuliang: number
  zhuanhua_shuliang: number
  zhuanhua_lv: number
  zhuangtai: string
  paixu: number
  miaoshu?: string
  created_at: string
  updated_at: string
}

export interface XiansuoLaiyuanCreate {
  laiyuan_mingcheng: string
  laiyuan_bianma: string
  laiyuan_leixing: string
  huoqu_chengben?: number
  zhuangtai?: string
  paixu?: number
  miaoshu?: string
}

export interface XiansuoLaiyuanUpdate {
  laiyuan_mingcheng?: string
  laiyuan_bianma?: string
  laiyuan_leixing?: string
  huoqu_chengben?: number
  zhuangtai?: string
  paixu?: number
  miaoshu?: string
}

// 线索状态
export interface XiansuoZhuangtai {
  id: string
  zhuangtai_mingcheng: string
  zhuangtai_bianma: string
  zhuangtai_leixing: string
  shangyige_zhuangtai?: string
  xiayige_zhuangtai?: string
  yanse_bianma: string
  tubiao_mingcheng?: string
  shi_zhongzhong_zhuangtai: string
  shi_chenggong_zhuangtai: string
  paixu: number
  zhuangtai: string
  miaoshu?: string
  created_at: string
  updated_at: string
}

export interface XiansuoZhuangtaiCreate {
  zhuangtai_mingcheng: string
  zhuangtai_bianma: string
  zhuangtai_leixing: string
  shangyige_zhuangtai?: string
  xiayige_zhuangtai?: string
  yanse_bianma?: string
  tubiao_mingcheng?: string
  shi_zhongzhong_zhuangtai?: string
  shi_chenggong_zhuangtai?: string
  paixu?: number
  zhuangtai?: string
  miaoshu?: string
}

// 线索跟进记录
export interface XiansuoGenjin {
  id: string
  xiansuo_id: string
  genjin_fangshi: string
  genjin_shijian: string
  genjin_neirong: string
  kehu_fankui?: string
  kehu_taidu?: string
  xiaci_genjin_shijian?: string
  xiaci_genjin_neirong?: string
  genjin_jieguo?: string
  genjin_ren_id: string
  genjin_ren_xingming?: string
  fujian_lujing?: string
  created_at: string
  updated_at: string
}

export interface XiansuoGenjinCreate {
  xiansuo_id: string
  genjin_fangshi: string
  genjin_shijian?: string
  genjin_neirong: string
  kehu_fankui?: string
  kehu_taidu?: string
  xiaci_genjin_shijian?: string
  xiaci_genjin_neirong?: string
  genjin_jieguo?: string
  fujian_lujing?: string
}

export interface XiansuoGenjinUpdate {
  genjin_fangshi?: string
  genjin_shijian?: string
  genjin_neirong?: string
  kehu_fankui?: string
  kehu_taidu?: string
  xiaci_genjin_shijian?: string
  xiaci_genjin_neirong?: string
  genjin_jieguo?: string
  fujian_lujing?: string
}

// 线索主表
export interface Xiansuo {
  id: string
  xiansuo_bianma: string
  gongsi_mingcheng: string
  lianxi_ren: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  hangye_leixing?: string
  gongsi_guimo?: string
  zhuce_dizhi?: string
  fuwu_leixing?: string
  yusuan_fanwei?: string
  shijian_yaoqiu?: string
  xiangxi_xuqiu?: string
  zhiliang_pinggu: string
  zhiliang_fenshu: number
  laiyuan_id: string
  laiyuan_xiangxi?: string
  xiansuo_zhuangtai: string
  fenpei_ren_id?: string
  fenpei_shijian?: string
  shouci_genjin_shijian?: string
  zuijin_genjin_shijian?: string
  xiaci_genjin_shijian?: string
  genjin_cishu: number
  shi_zhuanhua: string
  zhuanhua_shijian?: string
  zhuanhua_jine: number
  kehu_id?: string
  created_at: string
  updated_at: string
}

export interface XiansuoCreate {
  gongsi_mingcheng: string
  lianxi_ren: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  hangye_leixing?: string
  gongsi_guimo?: string
  zhuce_dizhi?: string
  fuwu_leixing?: string
  yusuan_fanwei?: string
  shijian_yaoqiu?: string
  xiangxi_xuqiu?: string
  zhiliang_pinggu?: string
  zhiliang_fenshu?: number
  laiyuan_id: string
  laiyuan_xiangxi?: string
}

export interface XiansuoUpdate {
  gongsi_mingcheng?: string
  lianxi_ren?: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  hangye_leixing?: string
  gongsi_guimo?: string
  zhuce_dizhi?: string
  fuwu_leixing?: string
  yusuan_fanwei?: string
  shijian_yaoqiu?: string
  xiangxi_xuqiu?: string
  zhiliang_pinggu?: string
  zhiliang_fenshu?: number
  laiyuan_id?: string
  laiyuan_xiangxi?: string
}

export interface XiansuoDetail extends Xiansuo {
  laiyuan?: XiansuoLaiyuan
  genjin_jilu_list: XiansuoGenjin[]
}

// 线索状态更新
export interface XiansuoStatusUpdate {
  xiansuo_zhuangtai: string
  beizhu?: string
}

// 线索分配更新
export interface XiansuoAssignUpdate {
  fenpei_ren_id: string
  beizhu?: string
}

// 线索统计
export interface XiansuoStatistics {
  total_xiansuo: number
  new_xiansuo: number
  following_xiansuo: number
  interested_xiansuo: number
  quoted_xiansuo: number
  won_xiansuo: number
  lost_xiansuo: number
  zhuanhua_lv: number
  pingjun_zhuanhua_zhouzqi: number
  pingjun_zhuanhua_jine: number
}

// 线索报价相关类型
export interface XiansuoBaojiaXiangmu {
  id: string
  baojia_id: string
  chanpin_xiangmu_id: string
  xiangmu_mingcheng: string
  shuliang: number
  danjia: number
  danwei: string
  xiaoji: number
  paixu: number
  beizhu?: string
  created_at: string
  updated_at: string
}

export interface XiansuoBaojia {
  id: string
  xiansuo_id: string
  baojia_bianma: string
  baojia_mingcheng: string
  zongji_jine: number
  baojia_zhuangtai: string
  youxiao_qi: string
  beizhu?: string
  is_expired: boolean
  xiangmu_list: XiansuoBaojiaXiangmu[]
  created_at: string
  updated_at: string
  created_by: string
}

export interface XiansuoBaojiaXiangmuInput {
  chanpin_xiangmu_id: string
  xiangmu_mingcheng?: string
  shuliang: number
  danjia?: number
  danwei?: string
  paixu?: number
  beizhu?: string
}

export interface XiansuoBaojiaCreate {
  xiansuo_id: string
  baojia_mingcheng: string
  youxiao_qi: string
  beizhu?: string
  xiangmu_list: XiansuoBaojiaXiangmuInput[]
}

export interface XiansuoBaojiaUpdate {
  baojia_mingcheng?: string
  youxiao_qi?: string
  baojia_zhuangtai?: string
  beizhu?: string
  xiangmu_list?: XiansuoBaojiaXiangmuInput[]
}

export interface XiansuoBaojiaListItem {
  id: string
  baojia_bianma: string
  baojia_mingcheng: string
  zongji_jine: number
  baojia_zhuangtai: string
  youxiao_qi: string
  is_expired: boolean
  xiangmu_count: number
  created_at: string
  created_by: string
}

export interface XiansuoInfoForBaojia {
  id: string
  gongsi_mingcheng: string
  lianxi_ren: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  kehu_id?: string
}

export interface XiansuoBaojiaDetail {
  id: string
  xiansuo_id: string
  baojia_bianma: string
  baojia_mingcheng: string
  youxiao_qi: string
  zongji_jine: number
  baojia_zhuangtai: string
  is_expired: boolean
  beizhu?: string
  xiangmu_list: XiansuoBaojiaXiangmu[]
  xiansuo_info: XiansuoInfoForBaojia
  created_at: string
  updated_at: string
  created_by: string
}

export interface XiansuoBaojiaListParams {
  page?: number
  size?: number
  xiansuo_id?: string
  baojia_zhuangtai?: string
  search?: string
}

export interface XiansuoBaojiaListResponse {
  items: XiansuoBaojiaListItem[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ChanpinFenleiOption {
  id: string
  fenlei_mingcheng: string
  chanpin_leixing: string
}

export interface ChanpinXiangmuOption {
  id: string
  xiangmu_mingcheng: string
  xiangmu_bianma: string
  yewu_baojia: number
  baojia_danwei: string
  banshi_tianshu: number
  fenlei_id: string
}

export interface ChanpinDataForBaojia {
  zengzhi_fenlei: ChanpinFenleiOption[]
  daili_jizhang_fenlei: ChanpinFenleiOption[]
  zengzhi_xiangmu: ChanpinXiangmuOption[]
  daili_jizhang_xiangmu: ChanpinXiangmuOption[]
}

// API 响应类型
export interface XiansuoListResponse {
  items: Xiansuo[]
  total: number
  page: number
  size: number
}

// 旧版兼容类型（如有遗留调用可逐步迁移）
export interface LegacyXiansuoBaojiaListResponse {
  items: XiansuoBaojia[]
  total: number
  page: number
  size: number
}

export interface XiansuoLaiyuanListResponse {
  items: XiansuoLaiyuan[]
  total: number
  page: number
  size: number
}

export interface XiansuoZhuangtaiListResponse {
  items: XiansuoZhuangtai[]
  total: number
  page: number
  size: number
}

export interface XiansuoGenjinListResponse {
  items: XiansuoGenjin[]
  total: number
  page: number
  size: number
}

// 查询参数类型
export interface XiansuoListParams {
  page?: number
  size?: number
  search?: string
  xiansuo_zhuangtai?: string
  laiyuan_id?: string
  fenpei_ren_id?: string
  zhiliang_pinggu?: string
  hangye_leixing?: string
  start_date?: string
  end_date?: string
}

export interface XiansuoLaiyuanListParams {
  page?: number
  size?: number
  search?: string
  laiyuan_leixing?: string
  zhuangtai?: string
}

export interface XiansuoGenjinListParams {
  page?: number
  size?: number
  xiansuo_id?: string
  genjin_ren_id?: string
  genjin_fangshi?: string
  start_date?: string
  end_date?: string
}
