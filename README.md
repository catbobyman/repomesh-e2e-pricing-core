# repomesh-e2e-pricing-core

RepoMesh 多仓交付验证夹具 —— **生产者仓库**。

拥有 storefront 的共享报价契约 `quote()`。两个消费者仓库依赖它：

- [repomesh-e2e-checkout](https://github.com/catbobyman/repomesh-e2e-checkout) —— 订单摘要
- [repomesh-e2e-billing](https://github.com/catbobyman/repomesh-e2e-billing) —— 发票渲染

## 当前需求（基线为红）

**报价支持多币种**：`quote()` 接受 `currency` 参数，`Quote` 携带 `currency` 字段，
消费者据此渲染。三个仓库都需要协同修改。

- 本仓单测：`python scripts/run_tests.py` —— 币种用例失败
- 跨仓联调：`python integration/run_joint_tests.py` —— 需要 `CHECKOUT_SRC` / `BILLING_SRC`
  指向两个消费者的 `src`，三仓全部改完才会通过

## 为什么需要联调测试

消费者的单测跑在 `contract/pricing_core.py`（冻结契约桩）上，因此消费者可以先于
生产者独立转绿。**三个仓库的单仓 CI 可以全绿，而组合仍然是坏的**——只有联调测试
按候选 SHA 同时检出三仓、用真实实现串起来，才能发现这类缺陷。这正是 RepoMesh
`ValidationSnapshot` 要解决的问题。

夹具刻意埋了一条**只有联调能看见的跨仓不变量**：零小数币种（JPY/KRW/VND）没有
辅币单位，应付金额必须取整。消费者对着契约桩测不到它（桩对取整规则保持沉默），
生产者的单测也覆盖不到它（本仓用例只验被要求的币种），因为它是**装配后系统的性质**。

于是完整故事有两轮：

| 轮次 | 三仓单测 | 联调 | 发生了什么 |
|---|---|---|---|
| 基线 | 全红 | 红 | 需求刚下发 |
| 第 1 轮：三仓各自完成币种透传 | **全绿** | **红** | `199.99 != 200.0`——门禁拦下 ChangeSet，产出返工任务 |
| 第 2 轮：生产者补齐按币种取整 | 全绿 | 绿 | 可以按顺序合并 |

第 1 轮那一格就是这套产品存在的理由：**每个仓库的验收都通过了，组合仍然是坏的**。

## 合并顺序

生产者必须先于消费者合并：消费者的新代码调用 `quote(currency=...)`，若先合并到
main，生产者尚未接受该参数，main 即刻损坏。回滚时顺序相反。
