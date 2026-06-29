param(
    [string]$BaseBranch = "main",
    [switch]$FetchOnly,
    [switch]$MergeToCurrentBranch
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path ".git")) {
    throw "当前目录不是 Git 仓库：$repoRoot"
}

$upstreamUrl = "https://github.com/royzhu121/archi_rule.git"
if (-not (git remote | Select-String -SimpleMatch "upstream")) {
    git remote add upstream $upstreamUrl
}

$status = git status --short
if ($status) {
    throw "当前存在未提交修改，请先提交或暂存后再同步 Roy 最新代码。"
}

git fetch upstream

if ($FetchOnly) {
    Write-Host "已完成 fetch：upstream/$BaseBranch" -ForegroundColor Green
    exit 0
}

$currentBranch = git branch --show-current

if ($MergeToCurrentBranch) {
    git merge "upstream/$BaseBranch"
    Write-Host "已将 upstream/$BaseBranch 合并到当前分支 $currentBranch" -ForegroundColor Green
    exit 0
}

if ($currentBranch -ne $BaseBranch) {
    throw "当前分支是 $currentBranch。请先切换到 $BaseBranch，或使用 -MergeToCurrentBranch。"
}

git merge "upstream/$BaseBranch"
Write-Host "已同步 Roy 最新代码到本地分支 $BaseBranch" -ForegroundColor Green