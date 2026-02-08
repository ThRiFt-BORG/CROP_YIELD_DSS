# Crop Yield DSS Frontend Setup Script
# This script creates the folder structure and empty placeholder files

Write-Host "Crop Yield DSS Frontend Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Get the script directory
$scriptPath = $PSScriptRoot
if ([string]::IsNullOrEmpty($scriptPath)) {
    $scriptPath = Get-Location
}

# Define the frontend folder path
$frontendPath = Join-Path $scriptPath "frontend"

# Ask user if they want to delete existing frontend folder
if (Test-Path $frontendPath) {
    Write-Host "WARNING: Frontend folder already exists at: $frontendPath" -ForegroundColor Yellow
    $response = Read-Host "Do you want to delete it and create a fresh one? (y/n)"
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Deleting existing frontend folder..." -ForegroundColor Yellow
        Remove-Item -Path $frontendPath -Recurse -Force
        Write-Host "Deleted!" -ForegroundColor Green
    } else {
        Write-Host "Operation cancelled. Exiting..." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "Creating folder structure..." -ForegroundColor Cyan

# Create directory structure
$directories = @(
    "frontend",
    "frontend/public",
    "frontend/src",
    "frontend/src/components",
    "frontend/src/services"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $scriptPath $dir
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    Write-Host "  [OK] Created: $dir" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Creating empty placeholder files..." -ForegroundColor Cyan

# Define all files to create
$files = @(
    "frontend/package.json",
    "frontend/public/index.html",
    "frontend/src/index.js",
    "frontend/src/index.css",
    "frontend/src/App.jsx",
    "frontend/src/App.css",
    "frontend/src/services/api.js",
    "frontend/src/components/Header.jsx",
    "frontend/src/components/Navigation.jsx",
    "frontend/src/components/Dashboard.jsx",
    "frontend/src/components/YieldChart.jsx",
    "frontend/src/components/FieldMap.jsx",
    "frontend/src/components/PredictionPanel.jsx",
    "frontend/src/components/DataUpload.jsx",
    "frontend/src/components/RasterAssets.jsx"
)

# Create empty files with helpful comments
foreach ($file in $files) {
    $fullPath = Join-Path $scriptPath $file
    $fileName = Split-Path $file -Leaf
    
    # Add a placeholder comment based on file type
    $extension = [System.IO.Path]::GetExtension($fileName)
    
    switch ($extension) {
        ".json" {
            $content = "// TODO: Copy content from artifact for $fileName"
        }
        ".html" {
            $content = "<!-- TODO: Copy content from artifact for $fileName -->"
        }
        ".js" {
            $content = "// TODO: Copy content from artifact for $fileName"
        }
        ".jsx" {
            $content = "// TODO: Copy content from artifact for $fileName"
        }
        ".css" {
            $content = "/* TODO: Copy content from artifact for $fileName */"
        }
        default {
            $content = "// TODO: Copy content from artifact for $fileName"
        }
    }
    
    Set-Content -Path $fullPath -Value $content
    Write-Host "  [OK] Created: $file" -ForegroundColor Gray
}

Write-Host ""
Write-Host "SUCCESS: Folder structure created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Copy content from each artifact into the corresponding file" -ForegroundColor White
Write-Host "  2. Navigate to frontend folder: cd frontend" -ForegroundColor White
Write-Host "  3. Install dependencies: npm install" -ForegroundColor White
Write-Host "  4. Start development: npm start" -ForegroundColor White
Write-Host "  OR run with Docker: docker-compose up --build" -ForegroundColor White
Write-Host ""
Write-Host "Files created at: $frontendPath" -ForegroundColor Cyan
Write-Host ""

# Create a README file with instructions
$readmePath = Join-Path $frontendPath "README_SETUP.txt"
$readmeContent = @"
CROP YIELD DSS - FRONTEND SETUP INSTRUCTIONS
=============================================

The folder structure has been created with placeholder files.

NEXT STEPS:
-----------

1. Copy content from the artifacts into each file:
   
   ✓ package.json
   ✓ public/index.html
   ✓ src/index.js
   ✓ src/index.css
   ✓ src/App.jsx
   ✓ src/App.css
   ✓ src/services/api.js
   ✓ src/components/Header.jsx
   ✓ src/components/Navigation.jsx
   ✓ src/components/Dashboard.jsx
   ✓ src/components/YieldChart.jsx
   ✓ src/components/FieldMap.jsx
   ✓ src/components/PredictionPanel.jsx
   ✓ src/components/DataUpload.jsx
   ✓ src/components/RasterAssets.jsx

2. Install dependencies:
   cd frontend
   npm install

3. Start the development server:
   npm start

4. OR use Docker:
   docker-compose up --build

FOLDER STRUCTURE:
-----------------
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── DataUpload.jsx
│   │   ├── FieldMap.jsx
│   │   ├── Header.jsx
│   │   ├── Navigation.jsx
│   │   ├── PredictionPanel.jsx
│   │   ├── RasterAssets.jsx
│   │   └── YieldChart.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.css
│   ├── App.jsx
│   ├── index.css
│   └── index.js
└── package.json

"@

Set-Content -Path $readmePath -Value $readmeContent
Write-Host "Setup instructions saved to: README_SETUP.txt" -ForegroundColor Green
Write-Host ""
Write-Host "Setup complete! Happy coding!" -ForegroundColor Green