@echo off
echo ===== 项目启动环境检查 =====
echo.
where node >nul 2>nul && (echo [OK] Node: & node -v) || echo [!!] 未检测到 Node.js
where python >nul 2>nul && (echo [OK] Python) || echo [!!] 未检测到 Python（请安装 3.11+）
where mysql >nul 2>nul && (echo [OK] MySQL) || echo [!!] 未检测到 MySQL
echo.
echo 提示：npm 脚本被 PowerShell 策略拦截时，请用 npm.cmd 或放行脚本策略。
pause
