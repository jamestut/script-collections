# fill this variable with path. To recursively list all tasks in a path, use the 
# "\Path\To\SchTask\" (e.g. ends with backslash).
# Otherwise, the last component of the name will be regarded as the task name.
$paths = @()

# populated by script
$tasks = @()

$paths | ForEach-Object {
    if(!$_.StartsWith("\")) {
        throw "Invalid path specification."
    }
    if($_.EndsWith("\")) {
        $tasks += Get-ScheduledTask -TaskPath ($_ + "*") -ErrorAction SilentlyContinue
    } else {
        $idx = $_.LastIndexOf("\")
        $path = $_.Substring(0, $idx + 1)
        $taskname = $_.Substring($idx + 1)
        $tasks += Get-ScheduledTask -TaskPath $path -TaskName $taskname -ErrorAction SilentlyContinue
    }
}
if(!$tasks.Length) {
    Write-Output "No matching task found."
}
$tasks | Disable-ScheduledTask
