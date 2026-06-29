# 协同工作流

本项目后续统一在以下目录继续修改：

`My tasks/07-租户二消审图（协同版本）/archi_rule-main`

## 远端说明

- `origin`：你的私有备份仓库
- `upstream`：Roy 的协同仓库

## 日常步骤

1. 只在 07 协同版目录修改代码。
2. 开始新一轮修改前，先同步 Roy 最新代码：

```powershell
.\pull_from_roy.ps1
```

3. 本地验证完成后，在项目根目录运行：

```powershell
.\push_to_roy_pr.ps1
```

4. 脚本会自动推送到 `upstream` 新分支，并创建 PR。
5. 在 GitHub 上检查 PR 内容，再通知 Roy 审阅或合并。

## 注意事项

- 不要直接在历史归档目录里改代码。
- 不要把 `biaozhun/` 下的大规范文件推到 GitHub。
- 若只是做私人备份，可以继续推 `origin`；若要协同，必须推 `upstream` 并开 PR。

## 常用命令

查看远端：

```powershell
git remote -v
```

拉取 Roy 最新代码：

```powershell
.\pull_from_roy.ps1
```

仅抓取 Roy 最新代码但不合并：

```powershell
.\pull_from_roy.ps1 -FetchOnly
```

仅推送到你的私有仓库：

```powershell
git push origin main
```