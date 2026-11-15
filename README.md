# district-flow-inference

用于匿名分区边际与抽样路径下的泊车流向重建的 Python 业务服务。当前版本提供来源读取、领域查询与资料概览，历史概览按内容寻址存档，不会被后续读取覆盖。统计研究与产品查询共用同一资料发布版本。

## 目录

- `district_flow/provider.py`：本地资料服务，保留独立 HTTP 来源契约与版本校验。
- `district_flow/client.py`：逐表分页读取，拒绝混合不同资料版本。
- `district_flow/partner.py`：领域查询接口，不代替统计推断。
- `district_flow/overview.py`：现有描述性概览。
- `district_flow/app.py`、`store.py`：业务查询与不可变概览存档。
- `data/release.json`：不含真实个人信息的本地演练资料。
- `docs/contracts.md`：领域与时间口径。

## 运行

Python 3.11，依赖固定在 `requirements.txt`。准备环境时执行 `python -m pip install -r requirements.txt`，正式运行不下载资料、包或模型。构建使用 `docker build -t district-flow-inference:local .`；该构建需要首次取得 Python 基础镜像及固定依赖。已经准备好的镜像可直接离线启动。

`python -m unittest discover -s tests -v` 运行来源、存档、领域与 HTTP 集成测试。`python -m compileall -q district_flow tests` 检查源码可编译性。

`python -m district_flow.demo` 会使用随机空闲端口启动两个真实 HTTP 进程内服务，读取资料、生成概览并核对存档，然后退出，正常耗时低于 10 秒。`docker run --rm --network none district-flow-inference:local` 执行同一流程。正式展示可在 90 秒内从干净目录启动并完整展示输出；这条命令当前展示的是已存在的概览。

长期运行时分别启动 `python -m district_flow.provider` 和 `python -m district_flow.app`，默认端口为 8091、8090。业务端可用 `SOURCE_URL` 指向独立来源，存档位置通过 `--database` 配置。查询 `/v1/summary` 获取概览，返回的 `report_id` 可通过 `/v1/reports/<report_id>` 读取。多个业务进程共享同一数据库时由 SQLite 事务协调写入。
