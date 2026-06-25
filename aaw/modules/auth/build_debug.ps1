param(
    [string]$SdkPath = "$env:LOCALAPPDATA\Android\Sdk",
    [string]$KotlinDir = "$env:USERPROFILE\scoop\apps\kotlin\2.3.21",
    [string]$ModuleDir = "$PSScriptRoot"
)

Write-Host "=== Build Nusuk Auth Debug APK ===" -ForegroundColor Cyan

# Paths
# Find latest platform
$platformDirs = Get-ChildItem "$SdkPath\platforms" -Directory | Sort-Object Name -Descending
$androidJar = Join-Path $platformDirs[0].FullName "android.jar"
$buildTools = "$SdkPath\build-tools\37.0.0"
$d8bat = "$buildTools\d8.bat"
$aapt2 = "$buildTools\aapt2.exe"
$apksigner = "$buildTools\apksigner.bat"

# Source directories — modules/auth/ is the single source of truth
$moduleSrc = "$ModuleDir\..\modules\auth\src"
$debugSrc = "$ModuleDir\src\main\java"
$resDir = "$ModuleDir\..\modules\auth\res"
$manifest = "$ModuleDir\src\main\AndroidManifest.xml"

# Output directories
$classesDir = "$ModuleDir\build\classes"
$dexDir = "$ModuleDir\build\dex"
$apkDir = "$ModuleDir\build\apk"
$resFlatDir = "$ModuleDir\build\res_flat"

New-Item -ItemType Directory -Path $classesDir -Force | Out-Null
New-Item -ItemType Directory -Path $dexDir -Force | Out-Null
New-Item -ItemType Directory -Path $apkDir -Force | Out-Null
New-Item -ItemType Directory -Path $resFlatDir -Force | Out-Null

# Kotlin stdlib
$kotlinStdlib = "$KotlinDir\lib\kotlin-stdlib.jar"
if (-not (Test-Path $kotlinStdlib)) { Write-Error "kotlin-stdlib.jar not found"; exit 1 }

# Find source files from both modules/auth/ (single source of truth) and debug wrapper
$authSrcFiles = Get-ChildItem -Path $moduleSrc -Recurse -Filter "*.kt" | Select-Object -ExpandProperty FullName
$debugSrcFiles = Get-ChildItem -Path $debugSrc -Recurse -Filter "*.kt" | Select-Object -ExpandProperty FullName
$srcFiles = $authSrcFiles + $debugSrcFiles
if (-not $srcFiles) { Write-Error "No Kotlin source files found"; exit 1 }
Write-Host "Source files:" -ForegroundColor Yellow
$srcFiles | ForEach-Object { Write-Host "  $_" }

# ========================
# Step 1: Compile Kotlin
# ========================
Write-Host "`n=== Step 1: Compiling Kotlin ===" -ForegroundColor Cyan

$compilerCp = @(
    "$KotlinDir\lib\kotlin-compiler.jar",
    "$KotlinDir\lib\kotlin-stdlib.jar",
    "$KotlinDir\lib\kotlin-reflect.jar",
    "$KotlinDir\lib\kotlin-script-runtime.jar",
    "$KotlinDir\lib\kotlin-daemon-client.jar",
    "$KotlinDir\lib\kotlin-preloader.jar"
) -join ";"

$sourceCp = "$androidJar;$kotlinStdlib"

$javaArgs = @(
    "-cp", $compilerCp
    "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler"
    "-cp", $sourceCp
    "-d", $classesDir
) + $srcFiles

Write-Host "Compiling Kotlin..."
$output = & java $javaArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $output
    Write-Error "Kotlin compilation failed (exit code: $LASTEXITCODE)"
    exit 1
}
Write-Host "Kotlin compilation succeeded!" -ForegroundColor Green

# ========================
# Step 2: Convert to DEX
# ========================
Write-Host "`n=== Step 2: Converting to DEX ===" -ForegroundColor Cyan

$dexOutputDir = "$dexDir\dex_output"
New-Item -ItemType Directory -Path $dexOutputDir -Force | Out-Null

$classFiles = Get-ChildItem -Path $classesDir -Recurse -Filter "*.class" | Select-Object -ExpandProperty FullName
if (-not $classFiles) { Write-Error "No class files generated"; exit 1 }
Write-Host "Class files: $($classFiles.Count)"

# Include kotlin-stdlib in DEX (needed for Kotlin runtime functions)
$d8Args = @(
    "--lib", $androidJar,
    "--min-api", "32",
    "--output", $dexOutputDir
) + $classFiles + @($kotlinStdlib)

Write-Host "Running d8..."
$d8Output = & $d8bat $d8Args 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $d8Output
    Write-Error "d8 conversion failed (exit code: $LASTEXITCODE)"
    exit 1
}

$dexOutput = "$dexOutputDir\classes.dex"
if (-not (Test-Path $dexOutput)) { Write-Error "DEX output not found"; exit 1 }
$size = (Get-Item $dexOutput).Length / 1KB
Write-Host "DEX generated: $([math]::Round($size, 1)) KB" -ForegroundColor Green

# ========================
# Step 3: Compile resources
# ========================
Write-Host "`n=== Step 3: Compiling Resources ===" -ForegroundColor Cyan

# Compile each resource using Python (directory mode for correct AAPT format)
$pythonScript = @"
import subprocess, sys, os, glob
aapt2 = r"$aapt2"
res_dir = r"$resDir"
flat_dir = r"$resFlatDir"
os.makedirs(flat_dir, exist_ok=True)

for root, dirs, files in os.walk(res_dir):
    for f in files:
        path = os.path.join(root, f)
        # Use directory mode: -o flat_dir, let aapt2 name the .flat file
        result = subprocess.run([aapt2, 'compile', '-o', flat_dir, path], capture_output=True, text=True)

print(f"Compiled resources to {flat_dir}")
"@
$scriptPath = "$env:TEMP\aapt2_compile.py"
[System.IO.File]::WriteAllText($scriptPath, $pythonScript)
$compileOut = & python $scriptPath 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $compileOut
    Write-Error "aapt2 compile failed"
    exit 1
}
Write-Host $compileOut

$flatFiles = Get-ChildItem -Path $resFlatDir -Filter "*.flat" | Select-Object -ExpandProperty FullName
Write-Host "Compiled $($flatFiles.Count) resources"

# ========================
# Step 4: Link APK
# ========================
Write-Host "`n=== Step 4: Linking APK ===" -ForegroundColor Cyan

$unsignedApk = "$apkDir\unsigned.apk"

$linkArgs = @(
    "-I", $androidJar
    "--manifest", $manifest
    "-o", $unsignedApk
    "--auto-add-overlay"
) + $flatFiles

# Use Python to run aapt2 link (avoids PowerShell parsing issues)
$flatFilesStr = ($flatFiles | ForEach-Object { "`"$_`"" }) -join " "
$pythonScript = @"
import subprocess, sys
aapt2 = r"$aapt2"
android_jar = r"$androidJar"
manifest = r"$manifest"
output = r"$unsignedApk"
flat_dir = r"$resFlatDir"
import os, glob
flats = glob.glob(os.path.join(flat_dir, '*.flat'))
cmd = [aapt2, 'link', '-I', android_jar, '--manifest', manifest, '-o', output, '--auto-add-overlay'] + flats
result = subprocess.run(cmd, capture_output=True, text=True)
sys.stdout.write(result.stdout)
if result.stderr: sys.stderr.write(result.stderr)
sys.exit(result.returncode)
"@
$scriptFile = "$env:TEMP\aapt2_link.py"
[System.IO.File]::WriteAllText($scriptFile, $pythonScript)
$linkOutput = python $scriptFile 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $linkOutput
    Write-Error "aapt2 link failed (exit code: $LASTEXITCODE)"
    exit 1
}
Write-Host $linkOutput

# ========================
# Step 5: Add DEX to APK
# ========================
Write-Host "`n=== Step 5: Adding DEX to APK ===" -ForegroundColor Cyan

# Use zip to add DEX to the APK (Python avoids zip corruption)
$pythonScript = @"
import zipfile, os, shutil, tempfile, sys
src = r"$unsignedApk"
dex = r"$dexOutput"
tmp = tempfile.NamedTemporaryFile(delete=False).name

with open(dex, 'rb') as f:
    dex_data = f.read()

with zipfile.ZipFile(src, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            zout.writestr(item, data)
        # Add classes.dex (rename from the output)
        info = zipfile.ZipInfo('classes.dex')
        info.compress_type = zipfile.ZIP_DEFLATED
        zout.writestr(info, dex_data)

shutil.move(tmp, src)
print(f"APK size: {os.path.getsize(src)} bytes")
"@
$scriptPath = "$env:TEMP\add_dex.py"
[System.IO.File]::WriteAllText($scriptPath, $pythonScript)
$pyOut = & python $scriptPath 2>&1
if ($LASTEXITCODE -ne 0) { Write-Error "DEX injection failed: $pyOut"; exit 1 }
Write-Host $pyOut -ForegroundColor Green

# ========================
# Step 6: Sign APK
# ========================
Write-Host "`n=== Step 6: Signing APK ===" -ForegroundColor Cyan

$signedApk = "$apkDir\NusukAuthDebug.apk"

# Copy unsigned as temporary signed (apksigner modifies in-place sometimes)
Copy-Item $unsignedApk "$apkDir\temp_unsigned.apk" -Force

$signArgs = @(
    "sign",
    "--ks", "$env:USERPROFILE\.android\debug.keystore",
    "--ks-pass", "pass:android",
    "--ks-key-alias", "androiddebugkey",
    "--v1-signing-enabled", "true",
    "--v2-signing-enabled", "true",
    "--v3-signing-enabled", "true",
    "--out", $signedApk,
    "$apkDir\temp_unsigned.apk"
)

Write-Host "Signing APK..."
$signOut = & $apksigner $signArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $signOut
    Write-Error "Signing failed"
    exit 1
}

# Clean up
Remove-Item "$apkDir\temp_unsigned.apk" -Force -ErrorAction SilentlyContinue

$apkSize = (Get-Item $signedApk).Length / 1MB
Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "APK: $signedApk ($([math]::Round($apkSize, 1)) MB)" -ForegroundColor Green

# ========================
# Step 7: Install
# ========================
Write-Host "`n=== Step 7: Installing ===" -ForegroundColor Cyan
& adb install -r "$signedApk" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Install success!" -ForegroundColor Green
} else {
    Write-Host "Install failed - try manual: adb install -r `"$signedApk`"" -ForegroundColor Red
}
