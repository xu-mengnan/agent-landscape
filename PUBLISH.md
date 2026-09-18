# 将本包发布到agent-landscape

初次发布曾被GitHub集成403阻止；恢复授权后的发布状态见[交付记录](docs/delivery-status.md)。以下保留为历史包的手动备用步骤，不代表需要再次应用补丁。当前仓库已包含研究文件时，请直接克隆并阅读、运行检查；不要重复应用初始补丁。不需要向聊天窗口提供token或密码。

## 安全补丁路线

在已有Git且正常登录GitHub的本地环境，使用一个干净的新克隆。将随交付提供的`agent-landscape-research-2026-09-18.patch`放在克隆目录的上一级：

```sh
git clone https://github.com/xu-mengnan/agent-landscape.git
cd agent-landscape
git status --short
git switch -c research/agent-landscape-2026-09-18
git apply --check ../agent-landscape-research-2026-09-18.patch
git apply ../agent-landscape-research-2026-09-18.patch
python scripts/run_checks.py
python scripts/validate_bundle.py
git status --short
git diff -- README.md
```

`--check`失败说明当前内容与补丁基线不一致，应先人工合并；不要加force，不要重置或覆盖用户已有改动。Windows上可按本机安装使用`py -3`替代`python`。

确认文件与测试结果后，才执行提交和推送：

```sh
git add README.md .gitignore PUBLISH.md docs sources benchmarks experiments tests results scripts templates
git diff --cached --stat
git commit -m "docs: add agent landscape research and offline reliability experiments"
git push -u origin research/agent-landscape-2026-09-18
```

随后在GitHub创建该分支到main的Pull Request并审阅。此文没有自动合并，也没有配置自动付费模型调用。目录包含发布失败的历史记录，实际成功发布后可补充新commit/PR信息，但不应抹去原始实验边界。

## 文件复制路线

也可将ZIP内文件复制到干净研究分支，审阅README改动及新增文件，再运行上述检查。不要把本地虚拟环境、`.git`、缓存、密钥或生产日志一起上传。
