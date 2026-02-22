import subprocess
import json


def query(date): 
    print ("getmooon")
    output = subprocess.check_output(["moontool", "--json", date])
    return json.loads(output)["calendar"]

def getMoons(year, month):
    '''
    generate all date of moon for current month;
    values are integer representing moon
    0: new moon
    1: firstQuarter
    2: fullMoon
    3: last quarter
    '''
    

    # print (json.dumps(moons, sort_keys=True, indent=4, separators=(',', ': ')))

    def isSameMonth(date):
        return year == int(date[0]) and month == int(date[1])

    map =  {
        "last_new_moon_utc": 0,
        "first_quarter_utc": 1,
        "full_moon_utc": 2,
        "last_quarter_utc": 3,
        "next_new_moon_utc": 0,
    }
    
    def date2arr(strDate):
        date = strDate.split("T")[0].split("-")
        return date


    def set_moons(moons): 
        for name in map.keys():
            date = moons[name]
            date = date2arr(date)
            if isSameMonth(date):
                out_moon["-".join(date)] = map[name]
                
    out_moon = {}


        

    query_date = "%2d-%02d-01" % (year, month)
    print ("query moon of:", query_date)
    moons = query(query_date)
    set_moons(moons)

    last_moon_date = date2arr(moons["next_new_moon_utc"])
    if isSameMonth(last_moon_date):
        query_date = "%d-%02d-%02d" % (year, month, int(last_moon_date[2])+1)
        moons = query(query_date)

        set_moons(moons)
    return out_moon
