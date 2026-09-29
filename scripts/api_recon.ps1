Write-Host ""
Write-Host "======================================="
Write-Host "       API SECURITY RECON"
Write-Host "======================================="

Write-Host ""
Write-Host "===== 1. HEALTH ENDPOINT ====="
curl.exe -i http://127.0.0.1:8000/health

Write-Host ""
Write-Host "===== 2. OPENAPI DISCOVERY ====="
curl.exe http://127.0.0.1:8000/openapi.json

Write-Host ""
Write-Host "===== 3. MISSING FILE TEST ====="
curl.exe -i -X POST "http://127.0.0.1:8000/predict"

Write-Host ""
Write-Host "===== 4. INVALID FILE TEST ====="
curl.exe -i -X POST "http://127.0.0.1:8000/predict" `
    -F "file=@test.txt"

Write-Host ""
Write-Host "======================================="
Write-Host "       RECON COMPLETE"
Write-Host "======================================="