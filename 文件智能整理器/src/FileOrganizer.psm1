# File Organizer for OpenClaw
# Provides functions to organize files by type, date, and size

$script:LastOperation = $null

function Get-FileTypeCategory {
    param([string]$Extension)
    
    $categories = @{
        # Images
        '.jpg' = 'Images'; '.jpeg' = 'Images'; '.png' = 'Images'; '.gif' = 'Images'
        '.bmp' = 'Images'; '.tiff' = 'Images'; '.svg' = 'Images'; '.webp' = 'Images'
        '.ico' = 'Images'; '.raw' = 'Images'; '.psd' = 'Images'
        
        # Documents
        '.txt' = 'Documents'; '.pdf' = 'Documents'; '.doc' = 'Documents'; '.docx' = 'Documents'
        '.xls' = 'Documents'; '.xlsx' = 'Documents'; '.ppt' = 'Documents'; '.pptx' = 'Documents'
        '.odt' = 'Documents'; '.ods' = 'Documents'; '.odp' = 'Documents'; '.rtf' = 'Documents'
        '.md' = 'Documents'; '.csv' = 'Documents'; '.json' = 'Documents'; '.xml' = 'Documents'
        
        # Archives
        '.zip' = 'Archives'; '.rar' = 'Archives'; '.7z' = 'Archives'; '.tar' = 'Archives'
        '.gz' = 'Archives'; '.bz2' = 'Archives'; '.iso' = 'Archives'
        
        # Audio
        '.mp3' = 'Audio'; '.wav' = 'Audio'; '.flac' = 'Audio'; '.aac' = 'Audio'
        '.ogg' = 'Audio'; '.m4a' = 'Audio'; '.wma' = 'Audio'
        
        # Video
        '.mp4' = 'Video'; '.avi' = 'Video'; '.mkv' = 'Video'; '.mov' = 'Video'
        '.wmv' = 'Video'; '.flv' = 'Video'; '.webm' = 'Video'
        
        # Executables
        '.exe' = 'Executables'; '.msi' = 'Executables'; '.bat' = 'Executables'
        '.cmd' = 'Executables'; '.ps1' = 'Executables'; '.sh' = 'Executables'
        
        # Code
        '.py' = 'Code'; '.js' = 'Code'; '.html' = 'Code'; '.css' = 'Code'
        '.java' = 'Code'; '.c' = 'Code'; '.cpp' = 'Code'; '.cs' = 'Code'
        '.php' = 'Code'; '.rb' = 'Code'; '.go' = 'Code'; '.rs' = 'Code'
        '.swift' = 'Code'; '.kt' = 'Code'
    }
    
    if ($categories.ContainsKey($Extension.ToLower())) {
        return $categories[$Extension.ToLower()]
    }
    return 'Other'
}

function Get-FileStats {
    <#
    .SYNOPSIS
        Get statistics about files in a folder
    #>
    param(
        [string]$Path = '.',
        [switch]$Recurse
    )
    
    if (-not (Test-Path $Path)) {
        Write-Error "Path not found: $Path"
        return
    }
    
    $files = Get-ChildItem -Path $Path -File -Recurse:$Recurse
    
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
    $totalCount = $files.Count
    
    $byType = $files | Group-Object { [System.IO.Path]::GetExtension($_.Name).ToLower() } |
        Select-Object @{N='Extension';E={$_.Name}}, Count, @{N='TotalSize';E={($_.Group | Measure-Object Length -Sum).Sum}} |
        Sort-Object Count -Descending
    
    $byCategory = $files | Group-Object { Get-FileTypeCategory([System.IO.Path]::GetExtension($_.Name)) } |
        Select-Object @{N='Category';E={$_.Name}}, Count, @{N='TotalSize';E={($_.Group | Measure-Object Length -Sum).Sum}} |
        Sort-Object Count -Descending
    
    return [PSCustomObject]@{
        Path = $Path
        TotalFiles = $totalCount
        TotalSize = $totalSize
        TotalSizeMB = [math]::Round($totalSize / 1MB, 2)
        ByExtension = $byType
        ByCategory = $byCategory
    }
}

function Sort-FilesByType {
    <#
    .SYNOPSIS
        Organize files into folders by file type
    #>
    param(
        [string]$Path = '.',
        [switch]$WhatIf,
        [string]$LogPath
    )
    
    if (-not (Test-Path $Path)) {
        Write-Error "Path not found: $Path"
        return
    }
    
    $files = Get-ChildItem -Path $Path -File
    $moves = @()
    
    foreach ($file in $files) {
        $category = Get-FileTypeCategory($file.Extension)
        $targetDir = Join-Path $Path $category
        $targetPath = Join-Path $targetDir $file.Name
        
        if (-not (Test-Path $targetDir)) {
            if (-not $WhatIf) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
        }
        
        $moves += [PSCustomObject]@{
            Source = $file.FullName
            Target = $targetPath
            Category = $category
        }
    }
    
    if ($WhatIf) {
        Write-Host "Would move $($moves.Count) files:" -ForegroundColor Yellow
        $moves | Group-Object Category | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Count) files"
        }
        return $moves
    }
    
    $moved = 0
    $failed = 0
    $log = @()
    
    foreach ($move in $moves) {
        try {
            if (Test-Path $move.Target) {
                Write-Warning "Target exists: $($move.Target)"
                $failed++
                continue
            }
            
            Move-Item -Path $move.Source -Destination $move.Target -Force
            $moved++
            $log += [PSCustomObject]@{
                Time = Get-Date
                Source = $move.Source
                Target = $move.Target
                Status = 'Success'
            }
        }
        catch {
            Write-Error "Failed to move $($move.Source): $_"
            $failed++
            $log += [PSCustomObject]@{
                Time = Get-Date
                Source = $move.Source
                Target = $move.Target
                Status = 'Failed'
                Error = $_.ToString()
            }
        }
    }
    
    $script:LastOperation = @{
        Time = Get-Date
        Type = 'SortByType'
        Path = $Path
        Moves = $log
        SuccessCount = $moved
        FailCount = $failed
    }
    
    if ($LogPath) {
        $log | Export-Csv -Path $LogPath -NoTypeInformation
    }
    
    Write-Host "Moved $moved files, $failed failed" -ForegroundColor Green
    return $script:LastOperation
}

function Sort-FilesByDate {
    <#
    .SYNOPSIS
        Organize files by modification date
    #>
    param(
        [string]$Path = '.',
        [ValidateSet('Year', 'Month')]
        [string]$GroupBy = 'Month',
        [switch]$WhatIf,
        [string]$LogPath
    )
    
    if (-not (Test-Path $Path)) {
        Write-Error "Path not found: $Path"
        return
    }
    
    $files = Get-ChildItem -Path $Path -File
    $moves = @()
    
    foreach ($file in $files) {
        $date = $file.LastWriteTime
        
        if ($GroupBy -eq 'Year') {
            $folderName = $date.ToString('yyyy')
        }
        else {
            $folderName = $date.ToString('yyyy-MM')
        }
        
        $targetDir = Join-Path $Path $folderName
        $targetPath = Join-Path $targetDir $file.Name
        
        if (-not (Test-Path $targetDir) -and -not $WhatIf) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        $moves += [PSCustomObject]@{
            Source = $file.FullName
            Target = $targetPath
            Date = $date
            Folder = $folderName
        }
    }
    
    if ($WhatIf) {
        Write-Host "Would move $($moves.Count) files:" -ForegroundColor Yellow
        $moves | Group-Object Folder | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Count) files"
        }
        return $moves
    }
    
    $moved = 0
    $failed = 0
    $log = @()
    
    foreach ($move in $moves) {
        try {
            if (Test-Path $move.Target) {
                Write-Warning "Target exists: $($move.Target)"
                $failed++
                continue
            }
            
            Move-Item -Path $move.Source -Destination $move.Target -Force
            $moved++
            $log += [PSCustomObject]@{
                Time = Get-Date
                Source = $move.Source
                Target = $move.Target
                Status = 'Success'
            }
        }
        catch {
            Write-Error "Failed to move $($move.Source): $_"
            $failed++
            $log += [PSCustomObject]@{
                Time = Get-Date
                Source = $move.Source
                Target = $move.Target
                Status = 'Failed'
                Error = $_.ToString()
            }
        }
    }
    
    $script:LastOperation = @{
        Time = Get-Date
        Type = 'SortByDate'
        Path = $Path
        GroupBy = $GroupBy
        Moves = $log
        SuccessCount = $moved
        FailCount = $failed
    }
    
    if ($LogPath) {
        $log | Export-Csv -Path $LogPath -NoTypeInformation
    }
    
    Write-Host "Moved $moved files, $failed failed" -ForegroundColor Green
    return $script:LastOperation
}

function Sort-FilesBySize {
    <#
    .SYNOPSIS
        Organize files by size categories
    #>
    param(
        [string]$Path = '.',
        [int[]]$Thresholds = @(1MB, 100MB, 1GB),
        [switch]$WhatIf,
        [string]$LogPath
    )
    
    if (-not (Test-Path $Path)) {
        Write-Error "Path not found: $Path"
        return
    }
    
    $files = Get-ChildItem -Path $Path -File
    $moves = @()
    
    foreach ($file in $files) {
        $size = $file.Length
        $category = if ($size -lt $Thresholds[0]) { 'Tiny' }
                   elseif ($size -lt $Thresholds[1]) { 'Small' }
                   elseif ($size -lt $Thresholds[2]) { 'Medium' }
                   else { 'Large' }
        
        $targetDir = Join-Path $Path $category
        $targetPath = Join-Path $targetDir $file.Name
        
        if (-not (Test-Path $targetDir) -and -not $WhatIf) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        $moves += [PSCustomObject]@{
            Source = $file.FullName
            Target = $targetPath
            Size = $size
            SizeMB = [math]::Round($size / 1MB, 2)
            Category = $category
        }
    }
    
    if ($WhatIf) {
        Write-Host "Would move $($moves.Count) files:" -ForegroundColor Yellow
        $moves | Group-Object Category | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Count) files"
        }
        return $moves
    }
    
    $moved = 0
    $failed = 0
    $log = @()
    
    foreach ($move in $moves) {
        try {
            if (Test-Path $move.Target) {
                Write-Warning "Target exists: $($move.Target)"
                $failed++
                continue
            }
            
            Move-Item -Path $move.Source -Destination $move.Target -Force
            $moved++
            $log += [PSCustomObject]@{
                Time = Get-Date
                Source = $move.Source
                Target = $move.Target
                Status = 'Success'
            }
        }
        catch {
            Write-Error "Failed to move $($move.Source): $_"
            $failed++
            $log += [PSCustomObject]@{
                Time = Get-Date
                Source = $move.Source
                Target = $move.Target
                Status = 'Failed'
                Error = $_.ToString()
            }
        }
    }
    
    $script:LastOperation = @{
        Time = Get-Date
        Type = 'SortBySize'
        Path = $Path
        Thresholds = $Thresholds
        Moves = $log
        SuccessCount = $moved
        FailCount = $failed
    }
    
    if ($LogPath) {
        $log | Export-Csv -Path $LogPath -NoTypeInformation
    }
    
    Write-Host "Moved $moved files, $failed failed" -ForegroundColor Green
    return $script:LastOperation
}

function Undo-LastSort {
    <#
    .SYNOPSIS
        Undo the last sorting operation
    #>
    param(
        [string]$Path
    )
    
    if (-not $script:LastOperation) {
        Write-Error "No previous operation to undo"
        return
    }
    
    if ($Path -and $script:LastOperation.Path -ne $Path) {
        Write-Error "Last operation was on different path: $($script:LastOperation.Path)"
        return
    }
    
    Write-Host "Undoing last operation from $($script:LastOperation.Time)" -ForegroundColor Yellow
    
    $restored = 0
    $failed = 0
    
    foreach ($move in $script:LastOperation.Moves) {
        if ($move.Status -eq 'Success') {
            try {
                if (Test-Path $move.Target) {
                    $targetDir = Split-Path $move.Source -Parent
                    if (-not (Test-Path $targetDir)) {
                        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                    }
                    Move-Item -Path $move.Target -Destination $move.Source -Force
                    $restored++
                }
            }
            catch {
                Write-Error "Failed to restore $($move.Target): $_"
                $failed++
            }
        }
    }
    
    Write-Host "Restored $restored files, $failed failed" -ForegroundColor Green
    $script:LastOperation = $null
}

# Export functions
Export-ModuleMember -Function Get-FileStats, Sort-FilesByType, Sort-FilesByDate, Sort-FilesBySize, Undo-LastSort
