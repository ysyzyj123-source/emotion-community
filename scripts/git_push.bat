@echo off
chcp 65001 >nul
REM ============================================================
REM  大学生情感互助系统 - 一键提交并推送到 GitHub
REM  用法：双击或命令行运行  scripts\git_push.bat "提交说明"
REM  示例：git_push.bat "实现回复与积分功能"
REM  若不带说明，则默认用当前日期作为提交信息
REM ============================================================

REM 切换到项目根目录（本脚本上级目录）
cd /d "%~dp0\.."

set MSG=%~1
if "%MSG%"=="" (
    set MSG=update %date% %time%
)

echo.
echo ===== 当前分支 =====
git branch --show-current
echo ===== 暂存所有改动 =====
git add -A
echo ===== 提交 =====
git commit -m "%MSG%"
echo ===== 推送到 GitHub (origin/main) =====
git push -u origin main

echo.
echo ===== 完成，当前状态 =====
git status -sb
echo.
echo 若提示需要认证：请在弹窗输入 GitHub 用户名 ysyzyj123-source，
echo 密码栏粘贴你的 Personal Access Token (ghp_ 或 github_pat_ 开头)。
pause
