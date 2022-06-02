file = open('minceraft.py', 'r')
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
             
newFile = open('converted.py', 'w')
print(newLines)
for i in newLines:
    newFile.write(i)
newFile.close

print(ord(' '))
