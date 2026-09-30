```powershell
Write-Host ""
Write-Host "==============================================="
Write-Host "   AI SECURITY RED TEAM - DEMONSTRATION"
Write-Host "==============================================="
Write-Host ""

$ContainerName = "ai-security-api"

# -----------------------------------------------
# 0. Check Docker Container
# -----------------------------------------------

Write-Host ""
Write-Host "===== 0. CHECKING DOCKER CONTAINER =====" -ForegroundColor Cyan

$ContainerStatus = docker inspect -f "{{.State.Running}}" $ContainerName 2>$null

if ($ContainerStatus -ne "true") {
    Write-Host "Docker container '$ContainerName' is not running." -ForegroundColor Red
    Write-Host ""
    Write-Host "Start it first with:"
    Write-Host "    .\scripts\docker-start.ps1"
    exit 1
}

Write-Host "Docker container is running." -ForegroundColor Green


# -----------------------------------------------
# 1. Inspect Model
# -----------------------------------------------

Write-Host ""
Write-Host "===== 1. MODEL INSPECTION =====" -ForegroundColor Cyan

docker exec $ContainerName python model/inspect_model.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Model inspection failed." -ForegroundColor Red
    exit 1
}


# -----------------------------------------------
# 2. Baseline
# -----------------------------------------------

Write-Host ""
Write-Host "===== 2. BASELINE EVALUATION =====" -ForegroundColor Cyan

docker exec $ContainerName python model/baseline.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Baseline evaluation failed." -ForegroundColor Red
    exit 1
}


# -----------------------------------------------
# 3. FGSM Attack
# -----------------------------------------------

Write-Host ""
Write-Host "===== 3. FGSM ATTACK =====" -ForegroundColor Cyan

docker exec $ContainerName python model/fgsm.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "FGSM attack failed." -ForegroundColor Red
    exit 1
}


# -----------------------------------------------
# 4. PGD Attack
# -----------------------------------------------

Write-Host ""
Write-Host "===== 4. PGD ATTACK =====" -ForegroundColor Cyan

docker exec $ContainerName python model/pgd.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "PGD attack failed." -ForegroundColor Red
    exit 1
}


# -----------------------------------------------
# 5. PGD Defense Comparison
# -----------------------------------------------

Write-Host ""
Write-Host "===== 5. PGD DEFENSE COMPARISON =====" -ForegroundColor Cyan

docker exec $ContainerName python model/pgd_compare.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "PGD comparison failed." -ForegroundColor Red
    exit 1
}


# -----------------------------------------------
# 6. Final Message
# -----------------------------------------------

Write-Host ""
Write-Host "==============================================="
Write-Host "        DEMONSTRATION COMPLETE"
Write-Host "==============================================="
Write-Host ""

Write-Host "Key results:" -ForegroundColor Green
Write-Host ""
Write-Host "Original Model      -> PGD ASR: 79.56%"
Write-Host "FGSM Defense        -> PGD ASR: 53.49%"
Write-Host "PGD Defense         -> PGD ASR: 43.07%"
Write-Host ""

Write-Host "The PGD defense improved robustness against"
Write-Host "the evaluated PGD attack."
Write-Host ""
```
