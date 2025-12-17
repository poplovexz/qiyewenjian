"""
支付回调API端点
"""
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import logging

from core.database import get_db
from services.zhifu_guanli.zhifu_huidiao_service import ZhifuHuidiaoService
from services.zhifu_guanli.zhifu_peizhi_service import ZhifuPeizhiService
from services.zhifu_guanli.zhifu_dingdan_service import ZhifuDingdanService
from services.zhifu_guanli.zhifu_tuikuan_service import ZhifuTuikuanService
from services.zhifu_guanli.zhifu_liushui_service import ZhifuLiushuiService
from models.zhifu_guanli.zhifu_tuikuan import ZhifuTuikuan
from models.zhifu_guanli.zhifu_liushui import ZhifuLiushui
from schemas.zhifu_guanli.zhifu_liushui_schemas import ZhifuLiushuiCreate
from utils.payment.weixin_pay import WeixinPayUtil
from utils.payment.weixin_pay_sandbox import WeixinPaySandboxUtil
from utils.payment.alipay import AlipayUtil, ALIPAY_SDK_AVAILABLE
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/weixin/notify", summary="微信支付回调")
async def weixin_payment_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    微信支付回调接口
    
    此接口由微信支付系统调用，用于通知支付结果
    不需要认证，但需要验证签名
    """
    huidiao_service = ZhifuHuidiaoService(db)
    peizhi_service = ZhifuPeizhiService(db)
    dingdan_service = ZhifuDingdanService(db)
    
    try:
        # 获取请求数据
        body = await request.body()
        body_str = body.decode('utf-8')
        headers = dict(request.headers)
        
        # 创建回调日志
        log = huidiao_service.create_log(
            huidiao_leixing='zhifu',
            zhifu_pingtai='weixin',
            qingqiu_url=str(request.url),
            qingqiu_fangfa='POST',
            qingqiu_tou=headers,
            qingqiu_shuju={'body': body_str},
            qianming=headers.get('wechatpay-signature', '')
        )
        
        try:
            # 解析回调数据（需要先验证签名）
            # 获取一个启用的微信支付配置用于验证签名
            peizhi_list = peizhi_service.get_list(
                page=1,
                page_size=1,
                peizhi_leixing='weixin',
                zhuangtai='qiyong'
            )
            
            if not peizhi_list.items:
                raise ValueError("未找到启用的微信支付配置")
            
            peizhi = peizhi_list.items[0]
            
            # 获取解密后的配置
            peizhi_detail = peizhi_service.get_detail(peizhi.id)

            # 检查是否为沙箱环境
            is_sandbox = peizhi_detail.huanjing == "shachang"

            if is_sandbox:
                # 沙箱环境使用API v2回调验证
                weixin_util = WeixinPaySandboxUtil(
                    appid=peizhi_detail.weixin_appid,
                    mch_id=peizhi_detail.weixin_shanghu_hao,
                    api_key=peizhi_detail.weixin_api_v3_miyao,
                    notify_url=peizhi_detail.tongzhi_url
                )

                # 验证签名
                callback_result = weixin_util.verify_notify(body_str)
            else:
                # 正式环境使用API v3回调验证
                weixin_util = WeixinPayUtil({
                    'weixin_appid': peizhi_detail.weixin_appid,
                    'weixin_shanghu_hao': peizhi_detail.weixin_shanghu_hao,
                    'weixin_shanghu_siyao': peizhi_detail.weixin_shanghu_siyao,
                    'weixin_zhengshu_xuliehao': peizhi_detail.weixin_zhengshu_xuliehao,
                    'weixin_api_v3_miyao': peizhi_detail.weixin_api_v3_miyao,
                    'tongzhi_url': peizhi_detail.tongzhi_url
                })

                # 验证签名并解密数据
                callback_result = weixin_util.callback(headers, body_str)

            if not callback_result.get('success'):
                # 签名验证失败
                huidiao_service.update_log_verification(
                    log.id,
                    qianming_yanzheng='shibai',
                    cuowu_xinxi=callback_result.get('message', '签名验证失败')
                )
                huidiao_service.update_log_result(
                    log.id,
                    chuli_zhuangtai='shibai',
                    cuowu_xinxi='签名验证失败'
                )

                # 沙箱环境返回XML格式
                if is_sandbox:
                    return Response(
                        content='<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名验证失败]]></return_msg></xml>',
                        media_type='application/xml'
                    )
                else:
                    return Response(
                        content=json.dumps({'code': 'FAIL', 'message': '签名验证失败'}),
                        media_type='application/json'
                    )
            
            # 签名验证成功
            huidiao_service.update_log_verification(log.id, qianming_yanzheng='chenggong')
            
            # 获取回调数据
            callback_data = callback_result.get('data', {})

            # 提取订单信息 (沙箱和正式环境字段名相同)
            out_trade_no = callback_data.get('out_trade_no')  # 商户订单号
            transaction_id = callback_data.get('transaction_id')  # 微信订单号

            # 交易状态 (沙箱环境使用result_code, 正式环境使用trade_state)
            if is_sandbox:
                trade_state = 'SUCCESS' if callback_data.get('result_code') == 'SUCCESS' else 'FAIL'
            else:
                trade_state = callback_data.get('trade_state')  # 交易状态

            if not out_trade_no:
                raise ValueError("回调数据中缺少商户订单号")

            # 查找订单
            dingdan = dingdan_service.get_by_dingdan_hao(out_trade_no)
            if not dingdan:
                raise ValueError(f"订单不存在: {out_trade_no}")

            # 更新订单状态
            if trade_state == 'SUCCESS':
                # 支付成功
                dingdan_service.update_status(
                    dingdan.id,
                    zhuangtai='paid',
                    disanfang_dingdan_hao=transaction_id
                )

                # 创建支付流水记录
                liushui_service = ZhifuLiushuiService(db)

                # 检查是否已经创建过流水记录（避免重复创建）
                existing_liushui = db.query(ZhifuLiushui).filter(
                    ZhifuLiushui.zhifu_dingdan_id == dingdan.id,
                    ZhifuLiushui.disanfang_dingdan_hao == transaction_id,
                    ZhifuLiushui.is_deleted == "N"
                ).first()

                if not existing_liushui:
                    # 获取交易金额
                    if is_sandbox:
                        # 沙箱环境直接从total_fee获取
                        total_amount = Decimal(callback_data.get('total_fee', 0)) / 100
                    else:
                        # 正式环境从amount对象获取
                        amount_data = callback_data.get('amount', {})
                        total_amount = Decimal(amount_data.get('total', 0)) / 100

                    # 获取支付账户(openid)
                    if is_sandbox:
                        # 沙箱环境从openid字段获取
                        zhifu_zhanghu = callback_data.get('openid', '')
                    else:
                        # 正式环境从payer对象获取
                        zhifu_zhanghu = callback_data.get('payer', {}).get('openid', '')

                    # 创建流水数据
                    liushui_data = ZhifuLiushuiCreate(
                        zhifu_dingdan_id=dingdan.id,
                        kehu_id=dingdan.kehu_id,
                        liushui_leixing="income",
                        jiaoyijine=total_amount,
                        shouxufei=Decimal('0.00'),  # 微信支付手续费通常在结算时扣除
                        shiji_shouru=total_amount,
                        zhifu_fangshi="weixin",
                        zhifu_zhanghu=zhifu_zhanghu,
                        disanfang_liushui_hao=transaction_id,
                        disanfang_dingdan_hao=transaction_id,
                        jiaoyishijian=datetime.now(),
                        liushui_zhuangtai="success",
                        duizhang_zhuangtai="pending"
                    )

                    try:
                        liushui_service.create_zhifu_liushui(liushui_data, "system")
                        logger.info(f"支付流水创建成功: {out_trade_no}")
                    except Exception as e:
                        logger.error(f"创建支付流水失败: {str(e)}")
                        # 流水创建失败不影响回调成功响应

                huidiao_service.update_log_result(
                    log.id,
                    chuli_zhuangtai='chenggong',
                    chuli_jieguo=json.dumps(callback_data, ensure_ascii=False)
                )

                logger.info(f"微信支付回调处理成功: {out_trade_no}")

                # 返回响应 (沙箱环境返回XML, 正式环境返回JSON)
                if is_sandbox:
                    return Response(
                        content='<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>',
                        media_type='application/xml'
                    )
                else:
                    return Response(
                        content=json.dumps({'code': 'SUCCESS', 'message': '成功'}),
                        media_type='application/json'
                    )
            else:
                # 其他状态
                huidiao_service.update_log_result(
                    log.id,
                    chuli_zhuangtai='chenggong',
                    chuli_jieguo=f"交易状态: {trade_state}"
                )

                # 返回响应
                if is_sandbox:
                    return Response(
                        content='<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>',
                        media_type='application/xml'
                    )
                else:
                    return Response(
                        content=json.dumps({'code': 'SUCCESS', 'message': '成功'}),
                        media_type='application/json'
                    )

        except Exception as e:
            logger.error(f"微信支付回调处理失败: {str(e)}")
            huidiao_service.update_log_result(
                log.id,
                chuli_zhuangtai='shibai',
                cuowu_xinxi=str(e)
            )

            # 返回错误响应
            # 注意: 这里的is_sandbox可能未定义,需要从peizhi获取
            try:
                if peizhi_detail and peizhi_detail.huanjing == "shachang":
                    return Response(
                        content=f'<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[{str(e)}]]></return_msg></xml>',
                        media_type='application/xml'
                    )
            except:
                pass

            return Response(
                content=json.dumps({'code': 'FAIL', 'message': str(e)}),
                media_type='application/json'
            )
            
    except Exception as e:
        logger.error(f"微信支付回调异常: {str(e)}")
        return Response(
            content=json.dumps({'code': 'FAIL', 'message': '系统异常'}),
            media_type='application/json'
        )


@router.post("/zhifubao/notify", summary="支付宝支付回调")
async def zhifubao_payment_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    支付宝支付回调接口
    
    此接口由支付宝系统调用，用于通知支付结果
    不需要认证，但需要验证签名
    """
    if not ALIPAY_SDK_AVAILABLE:
        return Response(
            content=json.dumps({'code': 'FAIL', 'message': '支付宝SDK不可用'}),
            media_type='application/json'
        )
    
    huidiao_service = ZhifuHuidiaoService(db)
    peizhi_service = ZhifuPeizhiService(db)
    dingdan_service = ZhifuDingdanService(db)
    
    try:
        # 获取请求数据
        form_data = await request.form()
        data_dict = dict(form_data)
        headers = dict(request.headers)
        
        # 创建回调日志
        log = huidiao_service.create_log(
            huidiao_leixing='zhifu',
            zhifu_pingtai='zhifubao',
            qingqiu_url=str(request.url),
            qingqiu_fangfa='POST',
            qingqiu_tou=headers,
            qingqiu_shuju=data_dict,
            qianming=data_dict.get('sign', '')
        )
        
        try:
            # 获取一个启用的支付宝配置用于验证签名
            peizhi_list = peizhi_service.get_list(
                page=1,
                page_size=1,
                peizhi_leixing='zhifubao',
                zhuangtai='qiyong'
            )
            
            if not peizhi_list.items:
                raise ValueError("未找到启用的支付宝配置")
            
            peizhi = peizhi_list.items[0]
            
            # 获取解密后的配置
            peizhi_detail = peizhi_service.get_detail(peizhi.id)
            
            # 初始化支付宝工具
            alipay_util = AlipayUtil(
                appid=peizhi_detail.zhifubao_appid,
                app_private_key=peizhi_detail.zhifubao_shanghu_siyao,
                alipay_public_key=peizhi_detail.zhifubao_zhifubao_gongyao,
                notify_url=peizhi_detail.tongzhi_url,
                debug=peizhi_detail.huanjing == 'shachang'
            )
            
            # 验证签名
            sign = data_dict.pop('sign', None)
            sign_type = data_dict.pop('sign_type', None)
            
            if not sign:
                raise ValueError("缺少签名")
            
            is_valid = alipay_util.verify_notify(data_dict, sign)
            
            if not is_valid:
                # 签名验证失败
                huidiao_service.update_log_verification(
                    log.id,
                    qianming_yanzheng='shibai',
                    cuowu_xinxi='签名验证失败'
                )
                huidiao_service.update_log_result(
                    log.id,
                    chuli_zhuangtai='shibai',
                    cuowu_xinxi='签名验证失败'
                )
                
                return Response(content='fail', media_type='text/plain')
            
            # 签名验证成功
            huidiao_service.update_log_verification(log.id, qianming_yanzheng='chenggong')
            
            # 提取订单信息
            out_trade_no = data_dict.get('out_trade_no')  # 商户订单号
            trade_no = data_dict.get('trade_no')  # 支付宝交易号
            trade_status = data_dict.get('trade_status')  # 交易状态
            
            if not out_trade_no:
                raise ValueError("回调数据中缺少商户订单号")
            
            # 查找订单
            dingdan = dingdan_service.get_by_dingdan_hao(out_trade_no)
            if not dingdan:
                raise ValueError(f"订单不存在: {out_trade_no}")
            
            # 更新订单状态
            if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                # 支付成功
                dingdan_service.update_status(
                    dingdan.id,
                    zhuangtai='paid',
                    disanfang_dingdan_hao=trade_no
                )

                # 创建支付流水记录
                liushui_service = ZhifuLiushuiService(db)

                # 检查是否已经创建过流水记录（避免重复创建）
                existing_liushui = db.query(ZhifuLiushui).filter(
                    ZhifuLiushui.zhifu_dingdan_id == dingdan.id,
                    ZhifuLiushui.disanfang_dingdan_hao == trade_no,
                    ZhifuLiushui.is_deleted == "N"
                ).first()

                if not existing_liushui:
                    # 获取交易金额
                    total_amount = Decimal(data_dict.get('total_amount', '0'))
                    buyer_pay_amount = Decimal(data_dict.get('buyer_pay_amount', '0'))

                    # 创建流水数据
                    liushui_data = ZhifuLiushuiCreate(
                        zhifu_dingdan_id=dingdan.id,
                        kehu_id=dingdan.kehu_id,
                        liushui_leixing="income",
                        jiaoyijine=total_amount,
                        shouxufei=Decimal('0.00'),  # 支付宝手续费通常在结算时扣除
                        shiji_shouru=total_amount,
                        zhifu_fangshi="zhifubao",
                        zhifu_zhanghu=data_dict.get('buyer_logon_id', ''),
                        disanfang_liushui_hao=trade_no,
                        disanfang_dingdan_hao=trade_no,
                        jiaoyishijian=datetime.now(),
                        liushui_zhuangtai="success",
                        duizhang_zhuangtai="pending"
                    )

                    try:
                        liushui_service.create_zhifu_liushui(liushui_data, "system")
                        logger.info(f"支付流水创建成功: {out_trade_no}")
                    except Exception as e:
                        logger.error(f"创建支付流水失败: {str(e)}")
                        # 流水创建失败不影响回调成功响应

                huidiao_service.update_log_result(
                    log.id,
                    chuli_zhuangtai='chenggong',
                    chuli_jieguo=json.dumps(data_dict, ensure_ascii=False)
                )

                logger.info(f"支付宝支付回调处理成功: {out_trade_no}")

                return Response(content='success', media_type='text/plain')
            else:
                # 其他状态
                huidiao_service.update_log_result(
                    log.id,
                    chuli_zhuangtai='chenggong',
                    chuli_jieguo=f"交易状态: {trade_status}"
                )
                
                return Response(content='success', media_type='text/plain')
                
        except Exception as e:
            logger.error(f"支付宝支付回调处理失败: {str(e)}")
            huidiao_service.update_log_result(
                log.id,
                chuli_zhuangtai='shibai',
                cuowu_xinxi=str(e)
            )
            
            return Response(content='fail', media_type='text/plain')
            
    except Exception as e:
        logger.error(f"支付宝支付回调异常: {str(e)}")
        return Response(content='fail', media_type='text/plain')


@router.post("/weixin/refund-notify", summary="微信退款回调")
async def weixin_refund_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    微信退款回调接口

    此接口由微信支付系统调用，用于通知退款结果
    不需要认证，但需要验证签名
    """
    huidiao_service = ZhifuHuidiaoService(db)

    try:
        # 获取请求数据
        body = await request.body()
        body_str = body.decode('utf-8')
        headers = dict(request.headers)

        # 创建回调日志
        log = huidiao_service.create_log(
            huidiao_leixing='tuikuan',
            zhifu_pingtai='weixin',
            qingqiu_url=str(request.url),
            qingqiu_fangfa='POST',
            qingqiu_tou=headers,
            qingqiu_shuju={'body': body_str},
            qianming=headers.get('wechatpay-signature', '')
        )

        try:
            # 处理退款回调（逻辑类似支付回调）
            # 这里简化处理，实际应该验证签名并更新退款状态
            huidiao_service.update_log_result(
                log.id,
                chuli_zhuangtai='chenggong',
                chuli_jieguo='退款回调处理成功'
            )

            logger.info("微信退款回调处理成功")

            return Response(
                content=json.dumps({'code': 'SUCCESS', 'message': '成功'}),
                media_type='application/json'
            )

        except Exception as e:
            logger.error(f"微信退款回调处理失败: {str(e)}")
            huidiao_service.update_log_result(
                log.id,
                chuli_zhuangtai='shibai',
                cuowu_xinxi=str(e)
            )

            return Response(
                content=json.dumps({'code': 'FAIL', 'message': str(e)}),
                media_type='application/json'
            )

    except Exception as e:
        logger.error(f"微信退款回调异常: {str(e)}")
        return Response(
            content=json.dumps({'code': 'FAIL', 'message': '系统异常'}),
            media_type='application/json'
        )


@router.post("/zhifubao/refund-notify", summary="支付宝退款回调")
async def zhifubao_refund_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    支付宝退款回调接口

    此接口由支付宝系统调用，用于通知退款结果
    不需要认证，但需要验证签名
    """
    huidiao_service = ZhifuHuidiaoService(db)

    try:
        # 获取请求数据
        form_data = await request.form()
        data_dict = dict(form_data)
        headers = dict(request.headers)

        # 创建回调日志
        log = huidiao_service.create_log(
            huidiao_leixing='tuikuan',
            zhifu_pingtai='zhifubao',
            qingqiu_url=str(request.url),
            qingqiu_fangfa='POST',
            qingqiu_tou=headers,
            qingqiu_shuju=data_dict,
            qianming=data_dict.get('sign', '')
        )

        try:
            # 处理退款回调（逻辑类似支付回调）
            # 这里简化处理，实际应该验证签名并更新退款状态
            huidiao_service.update_log_result(
                log.id,
                chuli_zhuangtai='chenggong',
                chuli_jieguo='退款回调处理成功'
            )

            logger.info("支付宝退款回调处理成功")

            return Response(content='success', media_type='text/plain')

        except Exception as e:
            logger.error(f"支付宝退款回调处理失败: {str(e)}")
            huidiao_service.update_log_result(
                log.id,
                chuli_zhuangtai='shibai',
                cuowu_xinxi=str(e)
            )

            return Response(content='fail', media_type='text/plain')

    except Exception as e:
        logger.error(f"支付宝退款回调异常: {str(e)}")
        return Response(content='fail', media_type='text/plain')

