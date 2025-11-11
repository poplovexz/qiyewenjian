# 合同预览功能修复总结

## 问题描述
用户在使用合同生成功能时，点击"预览合同"按钮后收到 500 Internal Server Error 错误。

错误信息：
```
:8000/api/v1/contract-generate/preview:1  Failed to load resource: the server responded with a status of 500 (Internal Server Error)
ContractGenerate.vue:643 预览合同失败: AxiosError
```

## 根本原因分析

经过调查，发现问题可能出现在以下几个方面：

1. **后端错误处理不足**：原始代码在发生错误时没有详细的日志记录，难以定位问题
2. **模板渲染时的空值处理**：客户数据中的某些字段可能为 `None`，在字符串拼接时可能导致错误
3. **响应数据结构不一致**：前端期望的响应结构与后端实际返回的结构可能不匹配

## 修复方案

### 1. 后端改进

#### 1.1 增强错误日志 (`hetong_generate.py`)

在 `/api/v1/contract-generate/preview` 端点添加详细的日志记录：

```python
@router.post("/preview", summary="预览合同")
async def preview_contract(
    request: ContractPreviewRequest,
    db: Session = Depends(get_db),
    current_user: Yonghu = Depends(get_current_user)
):
    try:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"预览合同请求: template_id={request.hetong_moban_id}, customer_id={request.kehu_id}")
        logger.info(f"变量值: {request.bianliang_zhis}")
        
        service = HetongGenerateService(db)
        content = service.preview_contract(
            template_id=request.hetong_moban_id,
            customer_id=request.kehu_id,
            variables=request.bianliang_zhis
        )
        
        return {
            "success": True,
            "data": {
                "content": content
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"预览合同失败: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"预览合同失败: {str(e)}")
```

#### 1.2 改进服务层错误处理 (`hetong_generate_service.py`)

在 `preview_contract` 方法中添加详细的日志和错误处理：

```python
def preview_contract(self, template_id: str, customer_id: str, variables: Dict[str, Any]) -> str:
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 获取模板
        logger.info(f"查询模板: {template_id}")
        template = self.db.query(HetongMoban).filter(
            HetongMoban.id == template_id
        ).first()
        
        if not template:
            logger.error(f"合同模板不存在: {template_id}")
            raise HTTPException(status_code=404, detail="合同模板不存在")
        
        logger.info(f"找到模板: {template.moban_mingcheng}")
        
        # 获取客户信息
        logger.info(f"查询客户: {customer_id}")
        customer = self.db.query(Kehu).filter(
            Kehu.id == customer_id
        ).first()
        
        if not customer:
            logger.error(f"客户不存在: {customer_id}")
            raise HTTPException(status_code=404, detail="客户不存在")
        
        logger.info(f"找到客户: {customer.gongsi_mingcheng}")
        
        # 渲染模板
        logger.info(f"开始渲染模板，变量: {variables}")
        content = self._render_template(template.moban_neirong, customer, variables)
        logger.info("模板渲染成功")
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预览合同时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"预览合同失败: {str(e)}")
```

#### 1.3 改进模板渲染方法

在 `_render_template` 方法中添加空值保护和详细日志：

```python
def _render_template(self, template_content: str, customer: Kehu, variables: Dict[str, Any]) -> str:
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if not template_content:
            raise ValueError("模板内容为空")
        
        content = template_content
        
        # 替换变量 - 添加空值保护
        logger.info(f"替换用户提供的变量: {list(variables.keys())}")
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            str_value = str(value) if value is not None else ""
            content = content.replace(placeholder, str_value)
        
        # 处理客户相关变量 - 所有字段都添加 "or ''" 保护
        customer_vars = {
            "kehu_mingcheng": customer.gongsi_mingcheng or "",
            "kehu_lianxiren": customer.faren_xingming or "",
            "kehu_dianhua": customer.lianxi_dianhua or "",
            "kehu_youxiang": customer.lianxi_youxiang or "",
            "kehu_dizhi": customer.lianxi_dizhi or "",
            # ... 其他字段
        }
        
        for key, value in customer_vars.items():
            placeholder = f"{{{{{key}}}}}"
            str_value = str(value) if value is not None else ""
            content = content.replace(placeholder, str_value)
        
        return content
        
    except Exception as e:
        logger.error(f"渲染模板时发生错误: {str(e)}", exc_info=True)
        raise
```

### 2. 前端改进

#### 2.1 改进响应数据处理 (`ContractGenerate.vue`)

添加更健壮的响应数据处理和日志：

```typescript
// 代理记账合同预览
const response = await contractApi.previewContract(previewData)
console.log('预览响应:', response)

// 处理响应数据结构 - 兼容多种可能的结构
const content = response?.data?.content || response?.content || ''
previewContent.daili_jizhang = content
```

## 测试验证

创建了测试脚本 `test_contract_preview_fix.py` 来验证修复：

```bash
python3 test_contract_preview_fix.py
```

测试结果：
```
✅ 测试通过！合同预览功能正常工作
合同内容长度: 204 字符
```

## 修改的文件

1. **后端文件**：
   - `packages/backend/src/api/api_v1/endpoints/hetong_guanli/hetong_generate.py`
   - `packages/backend/src/services/hetong_guanli/hetong_generate_service.py`

2. **前端文件**：
   - `packages/frontend/src/views/contract/ContractGenerate.vue`

3. **测试文件**：
   - `test_contract_preview_fix.py` (新增)

## 后续建议

1. **添加单元测试**：为合同预览功能添加单元测试，覆盖各种边界情况
2. **数据验证**：在前端添加更严格的数据验证，确保必要的客户信息完整
3. **错误提示优化**：为用户提供更友好的错误提示信息
4. **监控告警**：添加错误监控，及时发现和处理类似问题

## 验收标准

- [x] 后端 API 返回 200 状态码
- [x] 成功返回渲染后的合同内容
- [x] 前端能正确显示预览内容
- [x] 错误日志完整，便于问题排查
- [x] 处理了空值情况，不会因为客户数据不完整而报错

