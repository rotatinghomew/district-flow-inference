# 业务数据与接口

margins 的 in 表示目的区边际，out 表示起点区边际；count 为发布计数，tolerance 是来源允许的绝对误差，不是标准差。每个 window 的路网由 links 单独定义，allowed=false 是结构不可能，不是零样本。

paths 是抽样路径计数，capture_rate 属于设备抽样机会；其区名是观测区。confusion 给出 P(observed|actual)，行列方向不可倒置。缺少路径格子不代表没有流量。资料发布只含聚合值，没有个人链接键。

POST /v1/matrix-check 接收 revision、window、cells；返回结构零违例及各区与边际的差。该接口做规划输入校验，不会替调用方修改矩阵，也不计算统计估计。

## 资料发布

GET /v1/catalog 返回 revision、cutoff、settings 以及表名。GET /v1/tables/表名 按 revision、offset、limit 分页。默认 31 行，最多 100 行；next=null 表示结束。错误版本返回 409，参数错误返回 400，领域查询不可计算时返回 422。资料从 JSON 加载后对当前实例不可变；重启可换一个发布版本。

所有时间均为带 +08:00 的 ISO 8601 字符串，资料窗口用半开区间，只有免费时长阈值明确包含端点。计数为非负整数；null 表示未观察或未知，不等于零。来源分页顺序不是业务先后顺序。来源参数 revision 必须与资料一致。

业务服务现有 GET /v1/summary、GET /v1/reports/标识和 GET /health。概览保留 revision 和 cutoff，store.py 对规范 JSON 计算 SHA-256，内容相同重复读取不会产生不同标识。新的研究结果可独立扩展，不应改变现有概览指标的含义。
