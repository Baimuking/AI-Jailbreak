@echo off
REM pojia CLI 包装器：把仓库根目录加入 PATH 后即可用 `pojia ...`
python "%~dp0cli\pojia.py" %*
