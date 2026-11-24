# 원격 PC 화면 판정 — 화면 그대로 분 · 로그인 창 · 인증 기다림 · 앱 응답(그 PC 에 두고 hc exec 로 부름)
# UTF-8 BOM 으로 저장할 것(한글 마커를 쓰는 경우).
param([string]$Dir, [string]$AppLike = '*', [string]$LoginMarker = '', [string]$AuthWaitMarker = '')
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
New-Item -ItemType Directory -Force $Dir | Out-Null
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
[System.Drawing.Graphics]::FromImage($bmp).CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$crop = $bmp.Clone((New-Object System.Drawing.Rectangle 0, 0, $b.Width, ($b.Height - 48)), $bmp.PixelFormat)
$t = New-Object System.Drawing.Bitmap $crop, 32, 18
$sb = New-Object Text.StringBuilder
for ($y = 0; $y -lt 18; $y++) { for ($x = 0; $x -lt 32; $x++) { $c = $t.GetPixel($x, $y); [void]$sb.Append([char](65 + [int](($c.R + $c.G + $c.B) / 3 / 16))) } }
$h = $sb.ToString(); $st = Join-Path $Dir 'state.txt'; $now = Get-Date
$prev = if (Test-Path $st) { Get-Content $st } else { @() }
$same = 0
if ($prev.Count -ge 2) {
  $ph = $prev[0]; $diff = 0
  for ($i = 0; $i -lt [Math]::Min($h.Length, $ph.Length); $i++) { if ($h[$i] -ne $ph[$i]) { $diff++ } }
  if ($diff -le 2) { $same = [int]($now - [datetime]$prev[1]).TotalMinutes }
}
if ($same -eq 0) { Set-Content $st @($h, $now.ToString('o')) -Encoding ASCII }
$p = Join-Path $Dir ("s-" + $now.ToString('HHmmss') + ".jpg")
(New-Object System.Drawing.Bitmap $bmp, 640, ([int](640 * $b.Height / $b.Width))).Save($p, [System.Drawing.Imaging.ImageFormat]::Jpeg)
Get-ChildItem $Dir -Filter 's-*.jpg' | Sort-Object LastWriteTime -Descending | Select-Object -Skip 20 | Remove-Item -ErrorAction SilentlyContinue
$app = Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.ProcessName -like $AppLike } | Select-Object -First 1
$login = $false; $wait = $false
if ($app -and $LoginMarker) {
  try {
    Add-Type -AssemblyName UIAutomationClient
    $w = [Windows.Automation.AutomationElement]::FromHandle($app.MainWindowHandle)
    $N = [Windows.Automation.AutomationElement]::NameProperty
    $login = [bool]$w.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition($N, $LoginMarker)))
    if ($login -and $AuthWaitMarker) { $wait = [bool]$w.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition($N, $AuthWaitMarker))) }
  } catch {}
}
"SAME_MIN=$same LOGIN=$login AUTHWAIT=$wait APP=$([bool]$app) RESP=$($app.Responding) SHOT=$p"
