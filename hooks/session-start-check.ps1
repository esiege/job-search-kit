param([string]$PluginRoot)

$workspaceRoot = $env:CLAUDE_PROJECT_DIR
if (-not $workspaceRoot) { $workspaceRoot = (Get-Location).Path }

# The agent's cwd is the person's workspace, not this plugin's own install
# location - bundled files (scripts/templates/*, scripts/job_search/*, etc.)
# can't be found with a bare relative path. Pass the resolved plugin root
# through so skills/commands can construct absolute paths correctly. This
# is the one reliable channel for this - ${CLAUDE_PLUGIN_ROOT} substitution
# only happens in hooks.json's command string, not as something the agent
# can read directly via an env var during normal tool calls.
$pluginRootNote = ""
if ($PluginRoot) {
    $pluginRootNote = " This plugin's own bundled files (templates, scripts) live at `"$PluginRoot`" - use that as the base path whenever a skill or command references something like scripts/templates/X or scripts/job_search/Y.py, rather than treating it as relative to this workspace."
}

function Emit($context) {
    $out = @{
        hookSpecificOutput = @{
            hookEventName = "SessionStart"
            additionalContext = $context + $pluginRootNote
        }
    } | ConvertTo-Json -Depth 5
    Write-Output $out
    exit 0
}

$resumesDir = Join-Path $workspaceRoot "Resumes"
$masterResume = $null
if (Test-Path $resumesDir) {
    $masterResume = Get-ChildItem -Path $resumesDir -Filter "* - Master.txt" -File -ErrorAction SilentlyContinue | Select-Object -First 1
}

if (-not $masterResume) {
    Emit("This is a job-search-kit workspace with no master resume yet. Per the 'intake' skill: immediately ask the user whether they have source material ready (LinkedIn export, old resumes, project notes, cover letters, certifications - anything relevant) before doing anything else, and tell them to drop it in Intake/. Keep an encouraging, momentum-forward tone (see 'resume-tailoring' skill's checkpoint guidance) without ever treating silence as approval.")
}

$logPath = Join-Path $workspaceRoot "PDF_GENERATION_LOG.md"
$hasGeneralPdf = $false
if (Test-Path $logPath) {
    $logContent = Get-Content $logPath -Raw -ErrorAction SilentlyContinue
    if ($logContent -and ($logContent -match 'generate_pdf_general\.py' -or $logContent -match '-\s*General\.pdf')) {
        $hasGeneralPdf = $true
    }
}

if (-not $hasGeneralPdf) {
    Emit("A master resume text file exists ($($masterResume.Name)) but PDF_GENERATION_LOG.md shows no matching general/baseline PDF generated yet. Per the 'pdf-layout-standards' skill's sync rule: the .txt, generator script, and PDF should always exist together. Proactively offer to generate the PDF now as part of finishing this step - don't report the baseline as already finished just because the .txt exists.")
}

Emit("A master resume and its baseline PDF both exist for this workspace. Don't assume the user is finished with the baseline, though: always offer both continuing to refine the general resume and moving on to tailoring it for a real job posting, per the 'don't assume done' principle.")
