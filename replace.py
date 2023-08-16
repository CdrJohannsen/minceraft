file = open('src/mc_launch_old.py', 'r')
lines = file.readlines()
file.close()

newLines = []
for lineNum in range(len(lines)):
    newLines.append('')
    for characterNum in range(len(lines[lineNum])):
        if(ord(lines[lineNum][characterNum]) == 9):
            newLines[lineNum] += ('    ')
        else:
            newLines[lineNum] += lines[lineNum][characterNum]
             
newFile = open('src/mc_launch.py', 'w')
print(newLines)
for i in newLines:
    newFile.write(i)
newFile.close

print(ord(' '))
