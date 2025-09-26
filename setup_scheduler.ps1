# Windows 작업 스케줄러 설정 스크립트
# 관리자 권한으로 실행해야 합니다

Write-Host "환경부 무공해차 보조금 데이터 크롤링 작업 스케줄러 설정을 시작합니다..." -ForegroundColor Green

# 현재 디렉토리 경로
$currentPath = Get-Location
$scriptPath = Join-Path $currentPath "run_crawler.bat"

Write-Host "스크립트 경로: $scriptPath" -ForegroundColor Yellow

# 작업 스케줄러 작업 생성
$taskName = "EVSubsidyCrawler"
$taskDescription = "환경부 무공해차 보조금 데이터 크롤링 (매일 오전 9시 실행)"

try {
    # 기존 작업이 있으면 삭제
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "기존 작업을 삭제합니다..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    # 새 작업 생성
    $action = New-ScheduledTaskAction -Execute $scriptPath
    $trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription

    Write-Host "작업 스케줄러가 성공적으로 설정되었습니다!" -ForegroundColor Green
    Write-Host "작업명: $taskName" -ForegroundColor Cyan
    Write-Host "실행 시간: 매일 오전 9시" -ForegroundColor Cyan
    Write-Host "스크립트: $scriptPath" -ForegroundColor Cyan

    # 작업 상태 확인
    $task = Get-ScheduledTask -TaskName $taskName
    Write-Host "작업 상태: $($task.State)" -ForegroundColor Cyan

} catch {
    Write-Host "작업 스케줄러 설정 중 오류가 발생했습니다:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "관리자 권한으로 다시 실행해주세요." -ForegroundColor Yellow
}

Write-Host "`n작업 스케줄러 관리는 다음 명령어로 할 수 있습니다:" -ForegroundColor Yellow
Write-Host "작업 보기: Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
Write-Host "작업 실행: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
Write-Host "작업 삭제: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor White
