<#
    print-photo.ps1
    -----------------------------------------
    이미지 파일을 지정된 프린터로 인쇄 (세로 방향, A6 또는 4x6)
    - 비율 유지
    - 여백 최소화 (페이지 내 최대 크기)
    - 사진이 잘리지 않도록 자동 축소
    -----------------------------------------
    실행 예시 (CMD에서):
    powershell -NoProfile -ExecutionPolicy Bypass -File "C:\scripts\print-photo.ps1" -ImagePath "C:\images\photo.jpg" -PrinterName "EPSON PHOTO" -PaperSizePreset "4x6"
#>

param(
    [Parameter(Mandatory=$true)][string]$ImagePath,
    [Parameter(Mandatory=$true)][string]$PrinterName,
    [ValidateSet("4x6","A6")][string]$PaperSizePreset = "4x6"
)

# 어셈블리 로드
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Drawing.PrinterSettings

# 파일 확인
if (-not (Test-Path $ImagePath)) {
    Write-Error "이미지 파일을 찾을 수 없습니다: $ImagePath"
    exit 1
}

# 프린터 확인
$printers = [System.Drawing.Printing.PrinterSettings]::InstalledPrinters
if (-not ($printers -contains $PrinterName)) {
    Write-Error "프린터를 찾을 수 없습니다: $PrinterName"
    Write-Output "설치된 프린터: $($printers -join ', ')"
    exit 1
}

# 용지 크기 설정 (1/100 inch 단위)
switch ($PaperSizePreset) {
    "4x6" {
        $paperWidth  = [int](4.0 * 100)   # 400
        $paperHeight = [int](6.0 * 100)   # 600
    }
    "A6" {
        $paperWidth  = [int](4.133 * 100) # 413
        $paperHeight = [int](5.827 * 100) # 582
    }
}

# 이미지 로드
$image = [System.Drawing.Image]::FromFile($ImagePath)

# PrintDocument 생성
$doc = New-Object System.Drawing.Printing.PrintDocument
$doc.PrinterSettings.PrinterName = $PrinterName

# 사용자 정의 용지
$customPaper = New-Object System.Drawing.Printing.PaperSize("Custom", $paperWidth, $paperHeight)
$doc.DefaultPageSettings.PaperSize = $customPaper
$doc.DefaultPageSettings.Landscape = $false
$doc.PrintController = New-Object System.Drawing.Printing.StandardPrintController

# 인쇄 이벤트 정의
$doc.Add_PrintPage({
    param($sender, $e)

    # 페이지 전체 영역 사용 (여백 없음)
    $mb = $e.PageBounds

    # 이미지 비율 계산
    $imgW = $image.Width
    $imgH = $image.Height
    $pageW = $mb.Width
    $pageH = $mb.Height

    # 비율 유지하며 축소 (잘림 방지)
    $scaleX = $pageW / $imgW
    $scaleY = $pageH / $imgH
    $scale = [math]::Min($scaleX, $scaleY)

    # 실제 출력 크기
    $drawW = [int]([math]::Round($imgW * $scale))
    $drawH = [int]([math]::Round($imgH * $scale))

    # 중앙 정렬
    $x = [int]($mb.X + ($pageW - $drawW) / 2)
    $y = [int]($mb.Y + ($pageH - $drawH) / 2)

    # 고품질 보간
    $e.Graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $e.Graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $e.Graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality

    # 이미지 출력
    $e.Graphics.DrawImage($image, $x, $y, $drawW, $drawH)

    # 한 페이지만
    $e.HasMorePages = $false
})

# 인쇄 실행
try {
    $doc.Print()
    Write-Output "✅ 인쇄 완료: $ImagePath → $PrinterName ($PaperSizePreset, 세로)"
}
catch {
    Write-Error "❌ 인쇄 실패: $_"
}
finally {
    $image.Dispose()
    $doc.Dispose()
}
