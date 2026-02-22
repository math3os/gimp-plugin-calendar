import csv
import yaml
import os
__dirname = os.path.dirname(os.path.abspath(__file__))

def load_date_from_csv(filePath, date_year):
    with open(filePath) as csvFile:
        dates = {}
        reader = csv.reader(csvFile, dialect='excel', delimiter=';')
        dates = {}
        for row in reader:
            date, string = row
            year, month, day = date.split('-')
            if (year == "{year}"):
                year = date_year
            date = '%d-%02d-%02d' % (int(year), int(month), int(day))
            if date not in dates:
                dates[date] = []
            dates[date].append(string)
        return dates

def openPagesYaml():
    f = open('%s/../Pages.yaml' % (__dirname))
    return yaml.safe_load(f)


def replaceYearTemplate(dates,year):
    retDates = {}
    def append(date, string):
        if date not in retDates:
            retDates[date] = []
        retDates[date].append(string)

    for [date, string] in dates:
        isTemplate = False
        y, month, day = date.split('-')
        if ("{year}" == y):
            y = year
            isTemplate = True

        date = '%d-%02d-%02d' % (int(y), int(month), int(day))

        append(date, string)
        if isTemplate and int(month) == 12: # add tempated dates from december of previous year
            date = '%d-%02d-%02d' % (int(y)-1, int(month), int(day))
            append(date, string)
    return retDates

if __name__ == "__main__":
    yaml = openPagesYaml()
    res = replaceYearTemplate(yaml['dates'], '2023')
    print(res)
