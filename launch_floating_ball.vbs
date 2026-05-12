' Silent launcher for Claude Code Floating Ball
' Double-click this file to start the floating ball with no console window
CreateObject("WScript.Shell").Run "pyw """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\floating_ball.py""", 0, False
