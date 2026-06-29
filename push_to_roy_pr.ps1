param(
    [string]$BranchName = "",
    [string]$CommitMessage = "",
    [string]$BaseBranch = "main",
    [switch]$SkipPR
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

if (-not $BranchName) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmm"
    $BranchName = "tingting/$timestamp-firecheck-sync"
}

$status = git status --short
if (-not $status) {
    Write-Host "没有检测到未提交修改。" -ForegroundColor Yellow
    if (-not $SkipPR) {
        Write-Host "如需仅基于当前分支创建 PR，请手动执行 gh pr create。" -ForegroundColor Yellow
    }
    exit 0
}

$currentBranch = git branch --show-current
if ($currentBranch -ne $BranchName) {
    $existingBranch = git branch --list $BranchName
    if ($existingBranch) {
        git checkout $BranchName
    }
    else {
        git checkout -b $BranchName
    }
}

git add .

if (-not $CommitMessage) {
    $CommitMessage = "chore: sync collaborative updates $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

git commit -m $CommitMessage
git push -u upstream $BranchName

if (-not $SkipPR) {
    $title = $CommitMessage
    $body = @"
## Summary
- sync latest local changes from Tingting canonical 07 workspace

## Source
- My tasks/07-租户二消审图（协同版本）/archi_rule-main
"@
    gh pr create --repo royzhu121/archi_rule --base $BaseBranch --head $BranchName --title $title --body $body
}

Write-Host "完成。分支：$BranchName" -ForegroundColor Green