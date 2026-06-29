param(
    [string]$BaseBranch = "main",
    [string]$BranchName = "",
    [string]$CommitMessage = "",
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

$currentBranch = git branch --show-current
$status = git status --short
$hasLocalChanges = -not [string]::IsNullOrWhiteSpace($status)
$stashCreated = $false

if ($hasLocalChanges) {
    $stashMessage = "sync_with_roy_autostash_$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    git stash push --include-untracked -m $stashMessage | Out-Host
    $stashCreated = $true
}

try {
    if ($currentBranch -ne $BaseBranch) {
        git checkout $BaseBranch | Out-Host
    }

    & "$repoRoot\pull_from_roy.ps1" -BaseBranch $BaseBranch

    if (-not $BranchName) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmm"
        $BranchName = "tingting/$timestamp-firecheck-sync"
    }

    $existingBranch = git branch --list $BranchName
    if ($existingBranch) {
        git checkout $BranchName | Out-Host
    }
    else {
        git checkout -b $BranchName | Out-Host
    }

    if ($stashCreated) {
        git stash pop | Out-Host
    }

    $postStatus = git status --short
    if ([string]::IsNullOrWhiteSpace($postStatus)) {
        Write-Host "没有检测到需要提交的本地修改。" -ForegroundColor Yellow
        exit 0
    }

    if (-not $CommitMessage) {
        $CommitMessage = "chore: sync collaborative updates $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }

    & "$repoRoot\push_to_roy_pr.ps1" -BranchName $BranchName -CommitMessage $CommitMessage -BaseBranch $BaseBranch -SkipPR:$SkipPR
}
catch {
    if ($stashCreated) {
        Write-Host "发生错误，已保留自动暂存内容；可用 git stash list 检查。" -ForegroundColor Yellow
    }
    throw
}