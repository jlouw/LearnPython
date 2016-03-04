import csv

FILE_PATH = r"\\OLIFANT\Documents\GitHub\LearnPython"


def read_csv_file():
    yes_file = open(FILE_PATH + r"\yesVoters.csv", 'r+')
    yes_names = []

    for row in csv.reader(yes_file):
        yes_names.append(row)
        print(yes_names[-1])

    yes_file.close()
    return yes_names


def check_name(name):
    print("Name to check: " + name)
    if name in read_csv_file():
        print("Name already in list")
    else:
        print("Name not in list yet")


def import_names():

    print("\nRead new name txt file into a LIST:")
    new_file = open(FILE_PATH + r"\newnames.txt")
    new_names = []

    for line in new_file.readlines():
        names_and_surname = line.partition(' ')
        name = names_and_surname[0]
        rest = line.replace(name, "").replace('\\n', "").strip()
        new_names.append([name, rest])
        print(new_names[-1])

    print("\nRead csv file into a LIST:")
    yes_names = read_csv_file()

    print("\nSort the LIST from the csv file:")
    yes_names.sort(key=lambda x: x[1])

    for row in yes_names:
        print(row)

    print("\nFind diff between csn file LIST and txt file LIST:")
    diff = set(map(tuple, new_names)) - set(map(tuple, yes_names))
    print(("Yes: %i, New: %i, Diff %i") % (len(yes_names), len(new_names), len(diff)))

    for row in diff:
        print(row)

    print("\nWrite the unique names to the csv file\n")
    yes_file = open(FILE_PATH + r"\yesVoters.csv", 'r+')
    writer = csv.writer(yes_file, delimiter=',', lineterminator='\n')

    for newPerson in diff:
        writer.writerow(newPerson)

    new_file.close()


'''
Below here receives input from the command line
'''
import_names()
