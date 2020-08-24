if($args.Length -ne 1) {
    throw "This script requires file name."
}

# populated by script
$tasks = @()

Get-Content -Path $args[0] | ForEach-Object {
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
