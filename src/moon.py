import subprocess
import json

def getMoons(year, month):
    '''
    generate all date of moon for current month;
    values are integer representing moon
    0: new moon
    1: firstQuarter
    2: fullMoon
    3: last quarter
    '''
    moons = {}
    print ("BAAAM")
    date = "%s-%s-01" % (year, month)
    output = subprocess.check_output(["moontool", "--json", date])
    moons = json.loads(output)
    print (moons)
    print (json.dumps(moons, sort_keys=True, indent=4, separators=(',', ': ')))
    
    