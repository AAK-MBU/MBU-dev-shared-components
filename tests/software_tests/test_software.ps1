# Set variables
$repoUrl = "https://github.com/AAK-MBU/MBU-dev-shared-components.git"
$localPath = (Resolve-Path "$PSScriptRoot\..\..").Path
$testFolder = "tests/software_tests"
$venvPath = "$localPath\.venv"

# Clone or pull the repo
echo "Cloning git repo $repoUrl into $localPath"
if (Test-Path $localPath) {
    Set-Location $localPath
    git pull
} else {
    git clone $repoUrl $localPath
    Set-Location $localPath
}

# Create virtual environment if it doesn't exist
if (-Not (Test-Path $venvPath)) {
    python -m venv .venv
}

# Activate virtual environment
& "$venvPath\Scripts\Activate.ps1"

# Install the repo as a package
echo "Installing module"
try {
    $ErrorActionPreference = "Stop"
    python -m pip install --upgrade pip | out-null
    pip install -e . | out-null
    pip install -e .[dev] | out-null
} catch {
    Write-Error "An error occurred during pip install: $_"
    deactivate
    cd ..
    exit 1
}

echo "Running tests"
# Run pytest
python -m pytest --json-report --json-report-file="./$testFolder/pytest_report.json" $testFolder -p no:faulthandler

# Deactivate venv and return to main folder
deactivate
cd ..
