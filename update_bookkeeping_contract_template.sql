-- 更新代理记账合同模板
-- 将模板内容更新为新的"财税服务委托合同书"格式

UPDATE hetong_moban
SET 
    moban_mingcheng = '财税服务委托合同书',
    moban_neirong = '<div style="font-family: SimSun, serif; line-height: 1.8; padding: 20px;">
<h2 style="text-align: center; font-weight: bold; font-size: 18px; margin-bottom: 20px;">财税服务委托合同书</h2>

<p style="margin: 10px 0;"><strong>合同编号：</strong>{{ hetong_bianhao }}</p>
<p style="margin: 10px 0;"><strong>甲方：</strong>{{ jiafang_mingcheng }}</p>
<p style="margin: 10px 0;"><strong>乙方：</strong>{{ yifang_mingcheng }}</p>

<p style="margin: 15px 0; text-indent: 2em;">甲方因经营管理需要，委托乙方提供代理记账等财税服务。根据《中华人民共和国民法典》《代理记账管理办法》等法律法规的规定，经甲乙双方协商一致，签订以下协议：</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">一、代理期限</h3>
<p style="margin: 10px 0; text-indent: 2em;">经双方商定，服务时长1年，服务期总计自{{ fuwu_kaishi_riqi }}至{{ fuwu_jieshu_riqi }}</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">二、委托业务内容</h3>
<p style="margin: 10px 0;"><strong>1、服务套餐：</strong>甲方选择定制{{ fuwu_taocan }}的财税服务。(具体服务明细见附件)</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">三、服务方式、服务费用及付款方式</h3>
<p style="margin: 10px 0;"><strong>(一)服务方式：</strong></p>
<p style="margin: 10px 0; text-indent: 2em;">1.甲方提供记账用原始票据，乙方在乙方办公地运用财务软件记账并提供合同中约定的其它服务。</p>

<p style="margin: 10px 0;"><strong>(二)服务费用：</strong></p>
<p style="margin: 10px 0; text-indent: 2em;">1.服务费合同总金额：{{ hetong_zongjine }}元({{ hetong_zongjine_daxie }}元整),签订协议3日内支付合同金额{{ shoufu_jine }}元。乙方收款后应提供足额增值税发票。</p>

<p style="margin: 10px 0;"><strong>(三)付款方式：</strong></p>
<p style="margin: 10px 0; text-indent: 2em;">1.甲方同意按年付方式支付服务费；</p>
<p style="margin: 10px 0; text-indent: 2em;">2.账户名：{{ shoukuan_zhanghu_ming }} 账号：{{ shoukuan_zhanghao }} 开户行：{{ shoukuan_kaihuhang }}</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">四、甲方的责任和义务</h3>
<p style="margin: 10px 0;">1.甲方应建立健全的企业管理制度，依法经营、保证原始凭证的真实性、合法性、完整性。甲方应在每月5日前为乙方提供真实、完整的会计资料。如果甲方提供资料不全、或提供虚假会计资料，从而致使乙方无法继续工作，或导致工商、税务处罚的，由甲方负责。</p>
<p style="margin: 10px 0;">2.甲方应做好会计凭证传递过程中的登记和保管工作，提供的会计资料不符合规定的，甲方应更正、补充。甲方不配合核税，不配合提供申报资料，造成合同无法履行的，甲方已付费用不予退还。</p>
<p style="margin: 10px 0;">3.甲方应按本合同规定及时足额的支付代理记账费用。如甲方拖欠记账费30天（含本数）以上或联系不上甲方指定人员，乙方公司可停止提供服务且不视为违约，导致工商、税务处罚的，由甲方负责。</p>
<p style="margin: 10px 0;">4.除双方约定的费用外，如服务过程中乙方为甲方垫付行政服务费用、差旅费等费用，甲方应据实报销。</p>
<p style="margin: 10px 0;">5.甲方承诺在本协议生效期间或本协议结束后三年内，不得聘用乙方人员或业务人员；否则，向乙方支付违约金人民币【壹拾】万元整。</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">五、乙方的责任和义务</h3>
<p style="margin: 10px 0;">1.乙方应根据《中华人民共和国会计法》《企业会计制度》《小企业会计制度》及《企业会计准则》和地方各项税收管理等有关规定开展代理记账业务。</p>
<p style="margin: 10px 0;">2.乙方应根据甲方的会计核算制度，开展记账服务。</p>
<p style="margin: 10px 0;">3.乙方应设计会计凭证传递程序，做好交接会计资料、凭证签收工作，指导甲方按妥善保管会计档案，并在服务终止时办理会计工作交接手续。双方确认：首部记载的联系方式或双方另行确认的联系方式（包括微信、短信、邮件）方式进行的前述资料交接与实物交接具有相同效力。</p>
<p style="margin: 10px 0;">4.乙方应按有关规定审核甲方提供的原始凭证，填制记账凭证，登记会计账册，编制会计报表。同时乙方应妥善保管甲方的所有会计资料，由乙方原因造成甲方资料丢失，应由乙方负责弥补赔偿直接损失。</p>
<p style="margin: 10px 0;">5.乙方对工作中涉及的甲方商业机密和会计资料严格保密，不得随意向外透露、出示和传递。</p>
<p style="margin: 10px 0;">6.乙方对甲方提出的有关会计处理原则问题应当予以解释。</p>
<p style="margin: 10px 0;">7.甲方公司在服务期限内，性质发生改变或市场原因造成人力成本增加，乙方有权调整服务费用。</p>
<p style="margin: 10px 0;">8.乙方应于合同终止后，向甲方归还双方合作期间从甲方处取得的所有资料（包括原始凭证和记账的会计账簿），并提供相应报表、数据等；且告知甲方专管员的联系方式。</p>
<p style="margin: 10px 0;">9.服务过程中双方约定的应由乙方承担的权利或义务。</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">六、违约责任</h3>
<p style="margin: 10px 0;">1、合同存续期间，任何一方终止合同的，应提前二个月通知对方，并向对方支付总服务费30%的违约金。</p>
<p style="margin: 10px 0;">2、甲方逾期付款的，每逾期一日，应按逾期付款金额的0.1%计算，向乙方支付逾期付款的违约金。</p>
<p style="margin: 10px 0;">3、本合同终止（包括提前终止）之日起5日内，甲方应安排交接财务资料，变更乙方的财务联系人信息，逾期乙方有权自行处理甲方的财务资料。</p>
<p style="margin: 10px 0;">4、若甲方原因造成的税务申报或纳税延误，由甲方承担全部责任；反之，由乙方原因导致的延误其责任由乙方承担。</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">七、争议解决</h3>
<p style="margin: 10px 0; text-indent: 2em;">因执行本协议引起任何争议，由协议各方协商解决，也可由有关部门调解。协商或调解不成的，依法向本协议签订地（上海市长宁区）有管辖权的人民法院起诉。</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">八、通知与联系方式</h3>
<p style="margin: 10px 0;">1.甲乙双方通过本协议签约人或另行确认的联系人、邮箱、微信号、发出的文件均属于有效沟通文件。相关联系人利用指定邮箱、地址、微信号就有关委托事宜进行沟通及发送的文件，其内容表述亦可以作为双方履行委托事宜的依据。双方联系人、联系地址、联系邮箱或微信号或收款账户信息、开票信息的，应在变更后的3日内向对方发出通知（包括微信、短信、邮件方式）。</p>
<p style="margin: 10px 0;">2.本协议落款部分或双方另行确认的地址和联系电话等为有关本协议的任何通知、权利主张或法律文书（包括仲裁或诉讼文书）的送达地址与联系人。</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">九、其他</h3>
<p style="margin: 10px 0;">1.如任何法院或有权机关认为本协议的任何部分无效、不合法或不可执行，则该部分不应被认为构成本协议的一部分，但不应影响本协议其余部分的合法有效性及可执行性。</p>
<p style="margin: 10px 0;">2.声明：乙方系依甲方委托提供财务税务等系列咨询/代理服务，双方为委托关系。在服务过程中乙方依甲方委托为客户起草、撰写、整理的文件均已与甲方进行过充分沟通，且已获得甲方的确认或认可。乙方为甲方起草、撰写、整理的文件的基础信息与数据均由甲方提供，客户保证其提供的基础信息、数据、文件、证件等材料内容的真实性、完整性、合法性，并自愿承担因前述材料不真实、不完整或违反产生的全部责任。乙方对内容的整理与编写并不意味乙方赞同其观点或已经证实其内容的真实性、合法性。前述文件一经甲方确认并采用，甲方对文件中的数据、内容及信息承担相应法律责任。</p>
<p style="margin: 10px 0;">3.本协议一式二份，各方各执一份，每份具有同等效力。本协议经各方签章（企业盖章、自然人签字）之日起生效。本合同、附件及双方沟通过程中发送的经各方确认文件的扫描件与原件具有同等效力。</p>
<p style="margin: 10px 0;">4.协议未尽事宜，各方可以另行协商达成补充协议。补充协议与本协议的附件为本协议的组成部分，与本协议具有同等效力。</p>

<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">十、补充说明：</h3>
<p style="margin: 10px 0;">1、随着甲方业务量的增加，乙方有权调整收费，具体的收费标准双方可友好协商。如遇市场原因乙方调整服务价格的，甲方应按乙方新的服务收费标准向乙方支付服务费用。</p>
<p style="margin: 10px 0;">2、如甲方在合同期间有任何不满，请拨打投诉电话：13918291398。</p>

<div style="margin-top: 40px;">
    <table style="width: 100%; border: none;">
        <tr>
            <td style="width: 50%; text-align: left; border: none;">
                <p><strong>甲方（盖章/签字）：</strong>{{ jiafang_qianming }}</p>
                <p style="margin-top: 30px;">{{ jiafang_qianyue_riqi }}</p>
            </td>
            <td style="width: 50%; text-align: left; border: none;">
                <p><strong>乙方（盖章/签字）：</strong>{{ yifang_qianming }}</p>
                <p style="margin-top: 30px;">{{ yifang_qianyue_riqi }}</p>
            </td>
        </tr>
    </table>
</div>
</div>',
    bianliang_peizhi = '{
        "hetong_bianhao": {"label": "合同编号", "type": "string", "default": ""},
        "jiafang_mingcheng": {"label": "甲方名称", "type": "string", "default": ""},
        "yifang_mingcheng": {"label": "乙方名称", "type": "string", "default": "上海XX财务咨询有限公司"},
        "fuwu_kaishi_riqi": {"label": "服务开始日期", "type": "date", "default": ""},
        "fuwu_jieshu_riqi": {"label": "服务结束日期", "type": "date", "default": ""},
        "fuwu_taocan": {"label": "服务套餐", "type": "string", "default": ""},
        "hetong_zongjine": {"label": "合同总金额", "type": "number", "default": ""},
        "hetong_zongjine_daxie": {"label": "合同总金额大写", "type": "string", "default": ""},
        "shoufu_jine": {"label": "首付金额", "type": "number", "default": ""},
        "shoukuan_zhanghu_ming": {"label": "收款账户名", "type": "string", "default": ""},
        "shoukuan_zhanghao": {"label": "收款账号", "type": "string", "default": ""},
        "shoukuan_kaihuhang": {"label": "收款开户行", "type": "string", "default": ""},
        "jiafang_qianming": {"label": "甲方签名", "type": "string", "default": ""},
        "yifang_qianming": {"label": "乙方签名", "type": "string", "default": ""},
        "jiafang_qianyue_riqi": {"label": "甲方签约日期", "type": "date", "default": ""},
        "yifang_qianyue_riqi": {"label": "乙方签约日期", "type": "date", "default": ""}
    }',
    banben_hao = '2.0',
    beizhu = '财税服务委托合同书 - 2024年最新版本',
    updated_at = CURRENT_TIMESTAMP
WHERE moban_bianma = 'DLJZ_001' AND is_deleted = 'N';

