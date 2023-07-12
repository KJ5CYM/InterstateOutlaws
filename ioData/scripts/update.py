#!/usr/bin/python
import sys
import tarfile
import subprocess
import os
import time

#Needed since python < 2.5 doesn't have tar.extractall
def extracttar(tar, path="."):
    """Extract all members from the archive to the current working
        directory and set owner, modification time and permissions on
        directories afterwards. `path' specifies a different directory
        to extract to. `members' is optional and must be a subset of the
        list returned by getmembers().
    """
    directories = []

    for tarinfo in tar:
        if tarinfo.isdir():
            # Extract directory with a safe mode, so that
            # all files below can be extracted as well.
            try:
                os.makedirs(os.path.join(path, tarinfo.name), 0777)
            except EnvironmentError:
                pass
            directories.append(tarinfo)
        else:
            tar.extract(tarinfo, path)

    # Reverse sort directories.
    directories.sort(lambda a, b: cmp(a.name, b.name))
    directories.reverse()

    # Set correct owner, mtime and filemode on directories.
    for tarinfo in directories:
        path = os.path.join(path, tarinfo.name)
        try:
            tar.chown(tarinfo, path)
            tar.utime(tarinfo, path)
            tar.chmod(tarinfo, path)
        except tarfile.ExtractError, e:
            pass

print 'Preparing to update...'
if os.name == 'nt':
    try:
        subprocess.call(['taskkill', '/f', '/im', 'celstart.exe'])
        subprocess.call(['taskkill', '/f', '/im', 'celstart_static.exe'])
    except:
        pass
time.sleep(3)
#The start of the script
#For each of the tar files in the patch list,
#extract it and apply it
patchlist = open('patches/patches.txt', 'r')
for patch in patchlist:
    filename =  patch.strip()
    tar = tarfile.open('patches/%s' % filename)
    name, ext = filename.split('.tar')
    extracttar(tar, 'patches')
    patchfolder = 'patches/'+tar.getnames()[0].rstrip('/')
    tar.close()
    print 'applying patch', name
    if os.name == 'posix':
        subprocess.call(['python', patchfolder + '/' + 'ioApplyPatch.py'])
    else:
        subprocess.call([os.path.normpath(patchfolder + '/' + 'ioApplyPatch.bat')])
    print 'finished applying patch', name
print 'patching complete'
if os.name == 'posix':
    subprocess.call(['python', 'outlaws.py'])
else:
    subprocess.call(['outlaws.bat'])

