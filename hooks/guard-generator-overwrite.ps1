$stdin = [Console]::In.ReadToEnd()
$json = $stdin | ConvertFrom-Json
$toolName = $json.tool_name
$path = $json.tool_input.file_path
if (-not $path) { exit 0 }

$fileName = Split-Path $path -Leaf
$exists = Test-Path -LiteralPath $path -PathType Leaf

function Deny($reason) {
    $out = @{
        hookSpecificOutput = @{
            hookEventName = "PreToolUse"
            permissionDecision = "deny"
            permissionDecisionReason = $reason
        }
    } | ConvertTo-Json -Depth 5
    Write-Output $out
    exit 0
}

function Ask($reason) {
    $out = @{
        hookSpecificOutput = @{
            hookEventName = "PreToolUse"
            permissionDecision = "ask"
            permissionDecisionReason = $reason
        }
    } | ConvertTo-Json -Depth 5
    Write-Output $out
    exit 0
}

# Rule 1: never edit an existing generate_pdf_*.py / generate_docx_*.py in place.
# Edit always targets an existing file; Write only counts if the file is already there.
$isGeneratorScript = $fileName -match '^generate_(pdf|docx)_.*\.py$'
if ($isGeneratorScript -and ($toolName -eq 'Edit' -or ($toolName -eq 'Write' -and $exists))) {
    Deny("`"$fileName`" is an existing generator script. Never edit a generate_pdf_*.py / generate_docx_*.py in place - copy it to a new file named for this resume/theme instead (see PDF_GENERATION_LOG.md).")
}

# Rule 2: overwriting an existing resume .txt or .pdf requires explicit user confirmation.
$isResumeArtifact = $fileName -match '\.(txt|pdf)$' -and $path -match '[\\/]Resumes[\\/]'
if ($isResumeArtifact -and $exists -and $toolName -eq 'Write') {
    Ask("`"$fileName`" already exists in Resumes/. Confirm with the user before overwriting it.")
}

exit 0
