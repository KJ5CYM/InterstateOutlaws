#!/usr/bin/python
import os
import sys
import tarfile
import subprocess
sys.path.append('ioData/scripts')
import ioLoader

#Apply the patch
#This means entering all the subfolders
#and running xdelta against the files present
#Work out the folder we're in.
if os.name == 'posix':
    folderaslist = sys.argv[0].split('/')[:-1]
else:
    folderaslist = sys.argv[0].split('\\')[:-1]
foldername = '/'.join(folderaslist)
print foldername, sys.argv
try:
    rulesfile = open(foldername + '/patchrules.txt', 'r')
except IOError, error:
    print error
    print 'couldnt open patch rules file, skipping patch'
    sys.exit()
rules = ioLoader.parsefile(rulesfile.read())
rulesfile.close()
#Add new files.
if rules.has_key('Add'):
    for file in rules['Add']:
        #First open the file in the patch dir
        fileok = True
        try:
            copyfile = open('%s/%s' % (foldername, file), 'r')
        except IOError, error:
            fileok = False
            if error.errno is 2:
                print file, 'listed for adding, but doesnt exist in patch. Skipping'
            else:
                print 'Unhandled error in opening file', file
        #Now create the file in the destination
        if fileok:
            try:
                newfile = open(file, 'w')
            #Its folders don't exist, make them now
            except IOError, error:
                fileok = False
                if error.errno is 2:
                    path = file.split('/')
                    path = '/'.join(path[:len(path) - 1])
                    os.makedirs(path)
                    destfile = open(file, 'w')
                else:
                    print 'Unhandled error in copying file', file
            if fileok:
                newfile.write(copyfile.read())
                copyfile.close()
                newfile.close()
                print file, ' added'
#Remove old files
if rules.has_key('RemoveFiles'):
    for file in rules['RemoveFiles']:
        try:
            os.remove(file)
            print file, 'removed'
        except OSError, error:
            if error.errno is 2:
                print file, 'listed for deletion but doesnt exist. Skipping'
            else:
                print 'Unhandled error in deleting file', file
    
#Remove old folders
if rules.has_key('RemoveFolders'):
    for folder in rules['RemoveFolders']:
        #Empty out the folder bottom up
        for subroot, subfolders, subfiles in os.walk(folder, topdown = False):
            for subfile in subfiles:
                try:
                    os.remove('%s/%s' % (subroot, subfile))
                except:
                    print 'couldnt empty folder', subroot
                    break
            try:
                os.rmdir(subroot)
            except:
                print 'couldnt remove folder', subroot

#Now patch files
if rules.has_key('Patch'):
    for file in rules['Patch']:
        pfile = file + '-patched'
        command = 'utils/xdelta3'
        if os.name == 'nt':
            command += '.exe'
        #Run xdelta, producing the patched file 'filename-patched'
        if subprocess.call(['utils/xdelta3' ,'-f', '-d', '-s', file, os.path.normpath('%s/%s' % (foldername, file)), pfile]) is 0:
            #Now remove the original, and rename the patched file.
            try:
                os.remove(file)
            except:
                print 'couldnt remove file', file
            try:
                os.rename(pfile, file)
            except:
                print 'couldnt rename file', pfile
            print file, 'patched'