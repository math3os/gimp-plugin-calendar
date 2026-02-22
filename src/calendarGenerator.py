#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Gimp plugin to generate calendar for specific month
'''

from gimpfu import *
from cal import getMonthData
import calendar
import lune
import moon
import os
from util import openPagesYaml, replaceYearTemplate
import pagination
import pprint

__dirname = os.path.dirname(os.path.abspath(__file__))

firstweekday = 6 # sunday

cal = calendar.Calendar(firstweekday)


img_height = 2550
img_width = 3300
HEADER_HEIGHT = int(img_height / 7 * 1.5)
WEEKNAME_HEIGHT = int(HEADER_HEIGHT/3.2)
LINE_WIDTH = 4
MARGIN = 50
gray = (230, 230, 230, 1) #GRAY
black = (0,0,0,1)
MOON_DIAMETER = 100

weekDays = [
    'Dimanche',
    'Lundi',
    'Mardi',
    'Mercredi',
    'Jeudi',
    'Vendredi',
    'Samedi',
]

def calcDayDim(width, height):
    w = (width / 7) - LINE_WIDTH
    h = (height - HEADER_HEIGHT) / 5 - LINE_WIDTH
    return [int(w), int(h)]


def genDay(context, parent, day, width, height, halfDay, events):
    name = "day_%d" % (day)
    config = context['specs']['config']['dayNumber']
    font_size = config['fontSize']
    font_name = config['fontName']
    padding = config['padding']
    antialias = 1
    font_border = 1
    image = context['img']
    if halfDay:
        height = height / 2 - LINE_WIDTH
    layer_group = pdb.gimp_layer_group_new(image)
    layer_group.name = name
    pdb.gimp_image_insert_layer(image, layer_group, parent, 0)
    background = gimp.Layer(image, '%s_bg' % (name), width, height, RGB_IMAGE, 100, NORMAL_MODE)
    background.fill(FILL_WHITE)
    pdb.gimp_context_set_foreground(black)
    pdb.gimp_image_insert_layer(image, background, layer_group, 0)
    if day > 0:
        text_layer = pdb.gimp_text_fontname(image, background, padding, padding, day, font_border, antialias, font_size, POINTS, font_name)
        pdb.gimp_floating_sel_to_layer(text_layer)
        if events:
            addDayEvents(context, image, background, width, height, events)
    return layer_group

def addDayEvents(context, image, background, width, height, events):
    name = "dayEvent"
    config = context['specs']['config'][name]
    font_size = config['fontSize']
    font_name = config['fontName']
    antialias = 1
    font_border = 1
    padding = config['padding']
    justify = config['justify']
    if justify == "TEXT_JUSTIFY_RIGHT":
        justify = TEXT_JUSTIFY_RIGHT
    elif justify == "TEXT_JUSTIFY_LEFT":
        justify = TEXT_JUSTIFY_LEFT
    elif justify == "TEXT_JUSTIFY_CENTER":
        justify = TEXT_JUSTIFY_CENTER


    lineCount = len(events)
    for event in events: # add lineCount for long line
        if len(event) > 20:
            lineCount += 1
    text = '\n'.join(events)
    pos_h = height-50*lineCount - LINE_WIDTH

    wwidth, hheight, aascent, ddescent = pdb.gimp_text_get_extents_fontname(text, font_size, POINTS, font_name)
    text_layer = pdb.gimp_text_fontname(image, background, padding, pos_h, text, font_border, antialias, font_size, POINTS, font_name)
    pdb.gimp_floating_sel_to_layer(text_layer)
    pdb.gimp_text_layer_resize(text_layer, width-LINE_WIDTH - padding, 50*lineCount-LINE_WIDTH) # enlarge box to full width
    pdb.gimp_text_layer_set_justification(text_layer, justify)


# Generate all calendar's days
def genDays(context, calData):
    h_pos = HEADER_HEIGHT + LINE_WIDTH
    w_pos = LINE_WIDTH
    width = context['cellWidth']
    height = context['cellHeight']
    image = context['img']
    layer_group = pdb.gimp_layer_group_new(image)
    layer_group.name = "days"
    pdb.gimp_image_insert_layer(image, layer_group, context['parent'], 0)
    sixWeek = len(calData['week']) == 6 # we got a month 6 weeks long
    for idxWeek, week in enumerate(calData['week']):
        for index, day in enumerate(week):
            date = '%s-%02d-%02d' % (int(context['year']), int(context['month']), int(day))
            w_pos += width + LINE_WIDTH if index > 0 else MARGIN
            if sixWeek:
                if day == 0 and idxWeek == 5: continue # don't draw leftover days of month
                # halfDay: some day cell are split in two and shared with last days of months. That's when month is spreading on 6 weeks
                halfDay = (idxWeek == 4 and not calData['week'][5][index] == 0) or idxWeek == 5 and not day == 0
            else: halfDay = False
            events = None
            try:
                events = context['dates'][date]
            except KeyError:
                events = None
            layer = genDay(context, layer_group, day, width, height, halfDay, events)
            date = '%s-%02d-%02d' % (context['year'], context['month'], day)
            print(calData)
            if calData['moons'].has_key(date):
                print('moon:', date)
                moon = addMoon(image, calData['moons'][date])
                moon_w = width - MOON_DIAMETER - 20
                moon_h = 20
                pdb.gimp_image_insert_layer(image, moon, layer, 0)
                pdb.gimp_layer_translate(moon, moon_w, moon_h)
            _h_pos = h_pos - (height/2) - LINE_WIDTH if idxWeek == 5 else h_pos # 5th week is always on halfDays
            pdb.gimp_layer_translate(layer, w_pos, _h_pos)

        h_pos += height + LINE_WIDTH
        w_pos = LINE_WIDTH

def addMoon(image, moon):
    path = 'images'
    moons = [
        '0_newMoon.png',
        '1_firstQuarter.png',
        '2_fullMoon.png',
        '3_lastQuarter.png'
    ]
    layer = pdb.gimp_file_load_layer(image, __dirname + '/../' + path + '/' + moons[moon])
    return layer

def genHeader(context, monthName):
    previousYearMonthSuffix = context['specs']['config']['previousYearMonthSuffix']
    previousYear = True if context.has_key('previousYear') and context['previousYear'] == True else False
    name = "header"
    config = context['specs']['config'][name]
    font_size = config['fontSize']
    font_name = config['fontName']
    antialias = 1
    font_border = 1
    image = context['img']
    height = HEADER_HEIGHT - WEEKNAME_HEIGHT
    width = img_width-MARGIN*2
    layer_group = pdb.gimp_layer_group_new(image)
    layer_group.name = 'header'
    pdb.gimp_image_insert_layer(image, layer_group, context['parent'], 0)

    #background
    header = gimp.Layer(image, 'background_header', width, height, RGB_IMAGE, 100, NORMAL_MODE)
    header.fill(FILL_WHITE)
    pdb.gimp_image_insert_layer(image, header, layer_group, 0)
    pdb.gimp_layer_translate(header, int(MARGIN), int(0))
    # monthName
    try:
        _name = monthName
        if previousYear:
            _name = '%s-%s' % (_name, previousYearMonthSuffix)
        color = tuple(context['specs']['months'][_name]["weekBgColor"])
    except:
        color = (0,0,0)
    text_layer = pdb.gimp_text_fontname(image, header, int(img_width/2), int(height/3), monthName, font_border, antialias, font_size, POINTS, font_name)
    pdb.gimp_text_layer_set_color(text_layer, color)
    pdb.gimp_layer_translate(text_layer, int(text_layer.width/-2), 0)
    pdb.gimp_floating_sel_to_layer(text_layer)

    # logo
    logo = pdb.gimp_file_load_layer(image, __dirname + '/../images/logo.xcf')
    pdb.gimp_image_insert_layer(image, logo, layer_group, 0)
    pdb.gimp_layer_translate(logo, int(header.width/2/8),int(height/3) )

    weekDays_layer = genWeekdaySection(context)
    pdb.gimp_layer_translate(weekDays_layer, 0, HEADER_HEIGHT - WEEKNAME_HEIGHT)

def genWeekdaySection(context):
    previousYearMonthSuffix = context['specs']['config']['previousYearMonthSuffix']
    name = "weekDay"
    config = context['specs']['config'][name]
    previousYear = True if context.has_key('previousYear') and context['previousYear'] == True else False
    font_size = config['fontSize']
    font_name = config['fontName']
    antialias = 1
    font_border = 1
    try:
        monthName = context['name']
        if previousYear:
            monthName = '%s-%s' % (monthName, previousYearMonthSuffix)
        bgColor = tuple(context['specs']['months'][monthName]["weekBgColor"])
    except:
        bgColor = (0,0,0)

    justify = TEXT_JUSTIFY_CENTER
    image = context['img']
    cellWidth = context['cellWidth']
    layer_group = pdb.gimp_layer_group_new(image)
    layer_group.name = name
    pdb.gimp_image_insert_layer(image, layer_group, context['parent'], 0)
    for idx, dayName in enumerate(weekDays):
        background = gimp.Layer(image, '%s_bg' % (dayName), cellWidth+5, WEEKNAME_HEIGHT-LINE_WIDTH, RGB_IMAGE, 100, NORMAL_MODE)
        gimp.set_background(bgColor)
        background.fill(FILL_BACKGROUND)
        pdb.gimp_layer_translate(background, MARGIN + ((cellWidth + LINE_WIDTH)*idx), 0)
        pdb.gimp_image_insert_layer(image, background, layer_group, 0)
        text_layer = pdb.gimp_text_fontname(image, background, 0, 60, dayName, font_border, antialias, font_size, POINTS, font_name)
        pdb.gimp_text_layer_set_color(text_layer, (255, 255, 255))
        pos = (cellWidth + LINE_WIDTH)*idx
        pos = pos+config['paddingFirst'] if idx == 0 else pos # padding for the first weekday only
        pdb.gimp_layer_translate(text_layer, pos , 0)
        pdb.gimp_floating_sel_to_layer(text_layer)
        pdb.gimp_text_layer_resize(text_layer, cellWidth, 80)
        pdb.gimp_text_layer_set_justification(text_layer, justify)
    return layer_group


def generate_month(context, display = True):
    year = context['year']
    month = context['month']

    img = gimp.Image(img_width, img_height, RGB)

    # get calendar structure and name
    calData = getMonthData(year, month)
    monthName = calData['name']

    # create group for the month
    layer_group = pdb.gimp_layer_group_new(img)
    layer_group.name = monthName
    img.add_layer(layer_group, 0)

    # Background
    layer_background = gimp.Layer(img, "background", img_width, img_height, RGB_IMAGE, 100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(img, layer_background, layer_group, 0)
    pdb.gimp_context_set_background(gray)
    layer_background.fill(FILL_BACKGROUND)

    # cell dimensions
    [w, h] = calcDayDim(img_width-MARGIN*2, img_height-MARGIN)

    # prepare context
    context['img'] = img
    context['parent'] = layer_group
    context['cellWidth'] = w
    context['cellHeight'] = h
    context['name'] = monthName
    print ("year", year)
    calData['moons'] = moon.getMoons(year, month)

    genHeader(context, calData['name'])
    genDays(context, calData)

    #save file to ./build
    filename = "%s-%s-calendrier.xcf" % (year, context['name'].lower())
    path = '%s/../build/%s' % (__dirname, filename)
    pdb.gimp_xcf_save(0, img, layer_background, path, filename)

    # display if required
    if display: gimp.Display(img)
    return (img, layer_group)

def generate_calendar(date_year, date_month, fullYear):
    context = {

        'year': date_year,
        'month': date_month,
        'fullYear': fullYear,
        'specs': openPagesYaml()
    }
    context['dates'] = replaceYearTemplate(context['specs']['dates'], date_year)

    if fullYear:
        months = {}

        for month in range(1,13):
            context['month'] = month
            print "generating month %d" % month
            res = generate_month(context, display = False)
            name = "%s-calendrier" % context['name'].lower()
            months[name] = res
        # generate previous december
        context['year'] = date_year-1
        context['month'] = 12
        context['previousYear'] = True
        res = generate_month(context, display = False)
        name = "%s-calendrier" % context['name'].lower()
        months[name] = res
        pprint.pprint(months)
    else:
        generate_month(context)


register(
  "python-fu-gen-cal",
  'Calendar generator',
  'generate a calendar for specified month',
  "Mathieu Gagnon",
  "GPL License",
  "2022",
  "Generate Calendar",
  "",
  [
     (PF_INT, "date_year", "Year", 2024),
     (PF_INT, "date_month", "Month", 1),
     (PF_TOGGLE, "fullYear", "build full year ?", True)
  ],
  [],
  generate_calendar,
  menu="<Image>/cal"
  )

main()
