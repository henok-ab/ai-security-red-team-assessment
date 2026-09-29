Write-Host ""
Write-Host "==============================================="
Write-Host "     AI SECURITY RED TEAM - DOCKER START"
Write-Host "==============================================="
Write-Host ""

$image = "ai-security-red-team"
$container = "ai-security-api"
$port = "8000"

Write-Host "===== 1. Checking Docker ====="
docker info | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop is not running."
    exit 1
}

Write-Host "Docker is running."
Write-Host ""

Write-Host "===== 2. Building Docker image ====="
docker build -t $image .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker build failed."
    exit 1
}

Write-Host ""
Write-Host "===== 3. Removing old container ====="

docker stop $container 2>$null
docker rm $container 2>$null

Write-Host "Old container removed (if it existed)."
Write-Host ""

Write-Host "===== 4. Starting API container ====="

docker run -d `
    --name $container `
    -p "${port}:8000" `
    $image

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start container."
    exit 1
}

Write-Host ""
Write-Host "===== 5. Container status ====="
docker ps --filter "name=$container"

Write-Host ""
Write-Host "===== 6. Testing API ====="

Start-Sleep -Seconds 3

$response = curl.exe -s http://127.0.0.1:$port/health

if ($response -eq '{"status":"healthy"}') {
    Write-Host ""
    Write-Host "SUCCESS: API is healthy!"
} else {
    Write-Host ""
    Write-Host "WARNING: API health check returned:"
    Write-Host $response
}

Write-Host ""
Write-Host "==============================================="
Write-Host " API:  http://127.0.0.1:$port"
Write-Host " DOCS: http://127.0.0.1:$port/docs"
Write-Host "==============================================="
Write-Host ""

