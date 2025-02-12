# -*- coding: utf-8 -*-

import calendar

firstweekday = 6 # sunday

cal = calendar.Calendar(firstweekday)
months = [
    None,
    u'Janvier',
    u'Février',
    u'Mars',
    u'Avril',
    u'Mai',
    u'Juin',
    u'Juillet',
    u'Août',
    u'Septembre',
    u'Octobre',
    u'Novembre',
    u'Décembre'
]

def getMonthData(year, month):
    '''

    returns [
        name: monthName,
        week: [
            [0, 0, 1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10, 11, 12],
            [13, 14, 15, 16, 17, 18, 19],
            [20, 21, 22, 23, 24, 25, 26],
            [27, 28, 29, 30, 0, 0, 0]
        ]
    ]
    '''
    return {
        'name': months[month],
        'week': cal.monthdayscalendar(year,month),
    }
