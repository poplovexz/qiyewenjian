-- 创建审核管理权限的SQL脚本
-- 使用前请确保已连接到正确的数据库

-- 1. 创建审核管理权限
INSERT INTO quanxian (
    id, quanxian_ming, quanxian_bianma, miaoshu,
    ziyuan_leixing, ziyuan_lujing, zhuangtai,
    created_by, created_at, updated_at, is_deleted
) VALUES 
-- 审核菜单权限
(gen_random_uuid(), '审核管理菜单', 'audit_menu', '访问审核管理菜单的权限', 'menu', '/audit', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '审核任务管理', 'audit_manage', '管理审核任务的权限', 'menu', '/audit/tasks', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '审核流程配置', 'audit_config', '配置审核流程的权限', 'menu', '/audit/workflow-config', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '审核规则配置', 'audit_rule_config', '配置审核规则的权限', 'menu', '/audit/rule-config', 'active', 'system', NOW(), NOW(), 'N'),

-- 审核API权限
(gen_random_uuid(), '查看审核任务', 'audit:read', '查看审核任务列表和详情的权限', 'api', '/api/v1/audit/tasks', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '处理审核任务', 'audit:process', '处理审核任务的权限', 'api', '/api/v1/audit/process', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '合同审核', 'contract_audit', '审核合同的权限', 'api', '/api/v1/contracts/audit', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '报价审核', 'quote_audit', '审核报价的权限', 'api', '/api/v1/quotes/audit', 'active', 'system', NOW(), NOW(), 'N'),

-- 审核流程权限
(gen_random_uuid(), '查看审核流程', 'audit_workflow:read', '查看审核流程配置的权限', 'api', '/api/v1/audit/workflows', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '创建审核流程', 'audit_workflow:create', '创建审核流程的权限', 'api', '/api/v1/audit/workflows', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '编辑审核流程', 'audit_workflow:update', '编辑审核流程的权限', 'api', '/api/v1/audit/workflows', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '删除审核流程', 'audit_workflow:delete', '删除审核流程的权限', 'api', '/api/v1/audit/workflows', 'active', 'system', NOW(), NOW(), 'N'),

-- 审核规则权限
(gen_random_uuid(), '查看审核规则', 'audit_rule:read', '查看审核规则配置的权限', 'api', '/api/v1/audit/rules', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '创建审核规则', 'audit_rule:create', '创建审核规则的权限', 'api', '/api/v1/audit/rules', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '编辑审核规则', 'audit_rule:update', '编辑审核规则的权限', 'api', '/api/v1/audit/rules', 'active', 'system', NOW(), NOW(), 'N'),
(gen_random_uuid(), '删除审核规则', 'audit_rule:delete', '删除审核规则的权限', 'api', '/api/v1/audit/rules', 'active', 'system', NOW(), NOW(), 'N')

ON CONFLICT (quanxian_bianma) DO NOTHING;

-- 2. 为管理员角色分配审核权限
INSERT INTO jiaose_quanxian (id, jiaose_id, quanxian_id, created_by, created_at, updated_at, is_deleted)
SELECT 
    gen_random_uuid(),
    j.id,
    q.id,
    'system',
    NOW(),
    NOW(),
    'N'
FROM jiaose j
CROSS JOIN quanxian q
WHERE (j.jiaose_ming = '系统管理员' OR j.jiaose_ming = 'admin' OR j.jiaose_bianma = 'admin')
AND q.quanxian_bianma LIKE '%audit%'
AND NOT EXISTS (
    SELECT 1 FROM jiaose_quanxian jq 
    WHERE jq.jiaose_id = j.id AND jq.quanxian_id = q.id
);

-- 3. 更新现有权限为中文名称
UPDATE quanxian SET quanxian_ming = '查看用户', updated_at = NOW() WHERE quanxian_bianma = 'user:read';
UPDATE quanxian SET quanxian_ming = '创建用户', updated_at = NOW() WHERE quanxian_bianma = 'user:create';
UPDATE quanxian SET quanxian_ming = '编辑用户', updated_at = NOW() WHERE quanxian_bianma = 'user:update';
UPDATE quanxian SET quanxian_ming = '删除用户', updated_at = NOW() WHERE quanxian_bianma = 'user:delete';
UPDATE quanxian SET quanxian_ming = '查看角色', updated_at = NOW() WHERE quanxian_bianma = 'role:read';
UPDATE quanxian SET quanxian_ming = '创建角色', updated_at = NOW() WHERE quanxian_bianma = 'role:create';
UPDATE quanxian SET quanxian_ming = '编辑角色', updated_at = NOW() WHERE quanxian_bianma = 'role:update';
UPDATE quanxian SET quanxian_ming = '删除角色', updated_at = NOW() WHERE quanxian_bianma = 'role:delete';

UPDATE quanxian SET quanxian_ming = '查看客户', updated_at = NOW() WHERE quanxian_bianma = 'customer:read';
UPDATE quanxian SET quanxian_ming = '创建客户', updated_at = NOW() WHERE quanxian_bianma = 'customer:create';
UPDATE quanxian SET quanxian_ming = '编辑客户', updated_at = NOW() WHERE quanxian_bianma = 'customer:update';
UPDATE quanxian SET quanxian_ming = '删除客户', updated_at = NOW() WHERE quanxian_bianma = 'customer:delete';
UPDATE quanxian SET quanxian_ming = '客户管理', updated_at = NOW() WHERE quanxian_bianma = 'customer_manage';

UPDATE quanxian SET quanxian_ming = '查看线索', updated_at = NOW() WHERE quanxian_bianma = 'xiansuo:read';
UPDATE quanxian SET quanxian_ming = '创建线索', updated_at = NOW() WHERE quanxian_bianma = 'xiansuo:create';
UPDATE quanxian SET quanxian_ming = '编辑线索', updated_at = NOW() WHERE quanxian_bianma = 'xiansuo:update';
UPDATE quanxian SET quanxian_ming = '删除线索', updated_at = NOW() WHERE quanxian_bianma = 'xiansuo:delete';
UPDATE quanxian SET quanxian_ming = '分配线索', updated_at = NOW() WHERE quanxian_bianma = 'xiansuo:assign';
UPDATE quanxian SET quanxian_ming = '线索跟进', updated_at = NOW() WHERE quanxian_bianma = 'xiansuo:followup';

UPDATE quanxian SET quanxian_ming = '合同管理', updated_at = NOW() WHERE quanxian_bianma = 'contract_manage';
UPDATE quanxian SET quanxian_ming = '查看合同', updated_at = NOW() WHERE quanxian_bianma = 'contract:read';
UPDATE quanxian SET quanxian_ming = '创建合同', updated_at = NOW() WHERE quanxian_bianma = 'contract:create';
UPDATE quanxian SET quanxian_ming = '编辑合同', updated_at = NOW() WHERE quanxian_bianma = 'contract:update';
UPDATE quanxian SET quanxian_ming = '删除合同', updated_at = NOW() WHERE quanxian_bianma = 'contract:delete';
UPDATE quanxian SET quanxian_ming = '合同模板管理', updated_at = NOW() WHERE quanxian_bianma = 'contract_template_manage';

UPDATE quanxian SET quanxian_ming = '查看产品', updated_at = NOW() WHERE quanxian_bianma = 'product:read';
UPDATE quanxian SET quanxian_ming = '创建产品', updated_at = NOW() WHERE quanxian_bianma = 'product:create';
UPDATE quanxian SET quanxian_ming = '编辑产品', updated_at = NOW() WHERE quanxian_bianma = 'product:update';
UPDATE quanxian SET quanxian_ming = '删除产品', updated_at = NOW() WHERE quanxian_bianma = 'product:delete';

UPDATE quanxian SET quanxian_ming = '财务管理', updated_at = NOW() WHERE quanxian_bianma = 'finance_manage';
UPDATE quanxian SET quanxian_ming = '查看支付', updated_at = NOW() WHERE quanxian_bianma = 'payment:read';
UPDATE quanxian SET quanxian_ming = '创建支付', updated_at = NOW() WHERE quanxian_bianma = 'payment:create';
UPDATE quanxian SET quanxian_ming = '编辑支付', updated_at = NOW() WHERE quanxian_bianma = 'payment:update';

-- 4. 查看创建的审核权限
SELECT 
    quanxian_ming as "权限名称",
    quanxian_bianma as "权限编码", 
    ziyuan_leixing as "资源类型",
    ziyuan_lujing as "资源路径",
    miaoshu as "描述"
FROM quanxian 
WHERE quanxian_bianma LIKE '%audit%' 
ORDER BY ziyuan_leixing, quanxian_ming;

-- 5. 查看管理员角色的审核权限
SELECT 
    j.jiaose_ming as "角色名称",
    q.quanxian_ming as "权限名称",
    q.quanxian_bianma as "权限编码"
FROM jiaose j
JOIN jiaose_quanxian jq ON j.id = jq.jiaose_id
JOIN quanxian q ON jq.quanxian_id = q.id
WHERE (j.jiaose_ming = '系统管理员' OR j.jiaose_ming = 'admin' OR j.jiaose_bianma = 'admin')
AND q.quanxian_bianma LIKE '%audit%'
ORDER BY q.quanxian_ming;
