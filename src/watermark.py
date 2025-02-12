#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *



def watermark(config, image, props):

        def getLevel(level):
            if level == 0:
                return 'Maternelle'
            elif level == 1:
                return '1ʳᵉ année'
            else :
                return '%sᵉ année' % level

        width =  config['page']["width"] - config["watermark"]['position'][0]
        height = config["watermark"]['height']
        opacity = config["watermark"]['opacity']
        position = config["watermark"]['position']
        fontSize = config["watermark"]['fontSize']
        fontName = config["watermark"]['fontName']
        font_border = 1
        antialias = 1
        name = 'author'
        name = props['student']
        content = "%s\n %s\n %s" % (props['title'], name, getLevel(props['level']))

        layer_group = pdb.gimp_layer_group_new(image)
        layer_group.name = name
        image.add_layer(layer_group, 0)
        background = gimp.Layer(image, '%s_bg' % (name), width, height, RGB_IMAGE, opacity, NORMAL_MODE)
        background.fill(FILL_WHITE)
        pdb.gimp_context_set_foreground((0,0,0,1))
        pdb.gimp_image_insert_layer(image, background, layer_group, 0)
        pdb.gimp_layer_translate(background, position[0], position[1])

        text_layer = pdb.gimp_text_fontname(image, background, position[0], position[1], content, font_border, antialias, fontSize, POINTS, fontName)
        pdb.gimp_text_layer_resize(text_layer, width-config["watermark"]['padding'], height)
        pdb.gimp_text_layer_set_justification(text_layer, TEXT_JUSTIFY_RIGHT)
        pdb.gimp_floating_sel_to_layer(text_layer)

        