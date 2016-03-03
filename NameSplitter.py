import csv

print("\n********Read new name txt file into a LIST********")

newNamesFile = open(r'G:\Users\Jean\Documents\GitHub\LearnPython\newnames.txt')
newNames = []

for line in newNamesFile.readlines():
    fullnames = line.partition(' ')
    name = fullnames[0]
    rest = line.replace(name, "").replace('\\n', "").strip()
    newNames.append([name, rest])
    print(newNames[-1])


print("\n********Read csv file into a LIST********")
yesPath = "G:\\Users\\Jean\Documents\\GitHub\\LearnPython\\yesVoters.csv"
yesVotersFile = open(yesPath, 'r+')
yesVotersFileReader = csv.reader(yesVotersFile)
yesNames = []

for rowString in yesVotersFileReader:
    yesNames.append(rowString)
    print(yesNames[-1])


print("\n********Sort the LIST from the csv file********")

yesNames.sort(key=lambda x: x[1])

for rowString in yesNames:
    print(rowString)


print("\n********Find diff between csn file LIST and txt file LIST********")

diff = set(map(tuple, newNames)) - set(map(tuple, yesNames))
print(("Yes: %i, New: %i, Diff %i") % (len(yesNames), len(newNames), len(diff)))

for rowString in diff:
    print(rowString)


print("\n********Write the unique names to the csv file************")

yesWriter = csv.writer(yesVotersFile, delimiter=',', lineterminator='\n')

for newPerson in diff:
    yesWriter.writerow(newPerson)

newNamesFile.close()
yesVotersFile.close()
