@echo off
:: Launch Claude Code Floating Status Ball
:: Uses pythonw for silent launch (no console window)
cd /d "%~dp0"
start "" /B pyw "%~dp0floating_ball.py"
