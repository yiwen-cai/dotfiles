# 按需状态查询
先读本项目 ACCESS.md 与 ENVIRONMENTS.md，选择实际目标。通过 SSH 查询对应仓库 git status、最近进展文件、结果目录和日志。H100 历史路径是 $HOME/code/moe-test，A800 历史路径是 $HOME/moe_kv_cache_experiments；先确认路径仍存在。
报告采集时间、已完成/运行中/失败证据及未知项。模型是否下载、GPU 占用、依赖版本必须重新查询。不能将旧 Qwen3-8B“下载中”或“已就绪”描述当作当前状态。不要为了查询状态启动实验。
