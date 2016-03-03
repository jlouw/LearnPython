import csv

print("\n********Make a list of new names********")

newNamesFile = open(r'C:\Users\Jean\Desktop\CID\newnames.txt')
newNames = []

for line in newNamesFile.readlines():
    fullnames = line.partition(' ')
    name = fullnames[0]
    rest = line.replace(name, "").replace('\\n', "").strip()
    newNames.append([name, rest])
    print(newNames[-1])


print("\n********Make a list of old names********")

yesVotersFile = open(r'C:\Users\Jean\Desktop\CID\yesVoters.csv', 'r+')
yesVotersFileReader = csv.reader(yesVotersFile)
yesNames = []

for rowString in yesVotersFileReader:
    yesNames.append(rowString)
    print(yesNames[-1])

print("\n********Sorted********")

yesNames.sort(key=lambda x: x[1])

for rowString in yesNames:
    print(rowString)


print("\n********Get list of unique new names********")

newNamesTuple = set(map(tuple, newNames))
yesVotersTuple = set(map(tuple, yesNames))

diff = newNamesTuple - yesVotersTuple

print("yes " + str(len(yesVotersTuple)))
print("new " + str(len(newNamesTuple)))
print("diff " + str(len(diff)))

for rowString in diff:
    print(rowString)


print("\n********Add new names to yesVoters************")

yesWriter = csv.writer(yesVotersFile, delimiter=',', lineterminator='\n')

for newPerson in diff:
    yesWriter.writerow(newPerson)

newNamesFile.close()
yesVotersFile.close()
