﻿﻿﻿﻿## drvfs Mounter Script

This simple script can be used to automatically mount Windows volumes to a specified mountpoint inside WSL everytime a WSL instance is started. The list of volumes is specified in a file.

This script requires root access inside WSL to function. This script can be put in .bashrc on standard WSL installation to automatically mount the specified volume(s).

This script can be useful for automatically mounting Windows volumes with no drive letter(s) (but are mounted in one or more NTFS directories) inside WSL.

This script will not attempt to mount the specified drvfs device to a mountpoint that is already in use.

### Usage

`drvfs-mounter.sh <volumes_file>`

* `<volumes_file>`
 is the path to a list of mounted Windows volumes to be mounted. See next chapter for more information.

### Volumes List File

This file must meet the following criteria:

* Each line must be terminated with UNIX line ending.
* No preceding empty spaces on each line.
* No empty lines, except the last line.
* No comment line.

Each line is in the following format:

`<windows_mountpoint>;<target_WSL_mountpoint>`

Both `<target_WSL_mountpoint>` and `<windows_mountpoint>` may not contain spaces. `<target_WSL_mountpoint>` can be any empty directory in the WSL instance's root file system.

`<windows_mountpoint>` must use backslashes as the directory separator. Do not escape the backslashes. `<windows_mountpoint>` can be one of the following forms:

* Drive Letter (e.g. `D:`)
 WSL should automatically mount this kind of Windows volumes, but it can still be specified in this script.
* NTFS Directory Mountpoint (e.g. `C:\mnt\volume1`)
* UNC share (e.g. `\\server\share`)

### How It Works

This script will call:
`mount -t drvfs <windows_mountpoint> <target_WSL_mountpoint>`

should the target WSL mountpoint is not already used for mounting other devices. This script will automatically create the directory if not exists, but it does not check for permission clash or non-empty directory (the `mount` program should print the appropriate error message should an error happen).
