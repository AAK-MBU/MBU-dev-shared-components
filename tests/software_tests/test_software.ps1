# Set variables
$repoUrl = "https://github.com/AAK-MBU/MBU-dev-shared-components.git"
$localPath = (Resolve-Path "$PSScriptRoot\..\..").Path
$testFolder = "tests/software_tests"
$venvName = ".test_venv"
$venvPath = "$localPath\$venvName"

# pull the repo
echo "Pulling git repo $repoUrl into $localPath"
Set-Location $localPath
git pull


# Create virtual environment if it doesn't exist
if (-Not (Test-Path $venvPath)) {
    echo "Creating $venvName"
    python -m venv $venvName
}

# Activate virtual environment
echo "Activating $venvName"
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
    exit 1
}

echo "Running tests"
# Run pytest
python -m pytest --json-report --json-report-file="./$testFolder/pytest_report.json" $testFolder -p no:faulthandler

# Deactivate test_venv
deactivate