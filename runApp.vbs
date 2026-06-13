Set ws = CreateObject("WScript.Shell")
' 假设 runApp.ps1 跟本 .vbs 放在同一文件夹
ps1Path = ws.CurrentDirectory & "\runApp.ps1"
ws.Run "powershell -NoProfile -File """ & ps1Path & """", 1, False