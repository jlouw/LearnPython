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


def check_name(name_check):
    print("Name to check: " + name_check)
    for name, surname in read_csv_file():
        print()
        print(name + " " + surname, end="")
        if (name_check.lower() == surname.lower()):
            print("    +++++ Possible match +++++++", end="")


'''
Below here receives input from the command line
'''
check_name("du Toit")
