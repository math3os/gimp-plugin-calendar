#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import yaml
import util
import os
import re

from watermark import watermark

__dirname = os.path.dirname(os.path.abspath(__file__))
drawings = "%s/../Pages" % __dirname
build = "%s/../build" % __dirname
FILE_NOT_FOUND = 'not_found.xcf'

class Paginator():

    def __init__(self, config):
        self.config = config['config']
        self.pages = config['pages']
        self.year = config['year']
        self.assembled = config['assembled']
        self.verifyPages()

        if (self.assembled) :
            self.prepareAssembly()
        else:
            self.prepareOrdered()
        pdb.gimp_context_set_interpolation(INTERPOLATION_CUBIC)

    def verifyPages(self):
        if (len(self.pages) % 4 > 0):
            print('Page count must multiple of 4')

    def prepareOrdered(self):
        result = []
        for [i, page] in enumerate(self.pages):
            mod = i % 2

            if i == 1 or i == 0:
                result.append([page])
            else :
                last = result[-1]
                if len(last) == 1:
                    last.append(page)
                else:
                    result.append([page])
        self.assembly = result


    def prepareAssembly(self):
        middle = int(len(self.pages) / 2) - 1
        result = []
        counterUp = 0
        counterDown = len(self.pages) - 1

        while (counterDown > middle):
            recto_top = self.pages[counterUp]
            recto_bottom = self.pages[counterDown]

            # the very last page could be reversed for look but not yet
            recto_top['reverse'] = True
            recto_bottom['reverse'] = True
            if counterDown == len(self.pages) - 1:
                recto_bottom['reverse'] = False

            counterDown -= 1
            counterUp += 1

            verso_top = self.pages[counterUp]
            verso_bottom = self.pages[counterDown]

            verso_top['reverse'] = False
            verso_bottom['reverse'] = False

            counterDown -= 1
            counterUp += 1

            result.append([recto_top, recto_bottom])
            result.append([verso_top, verso_bottom])
        self.assembly = result
        return self

    def assemble(self, layers = None):
        exts = ['xcf', 'png']
        pageConfig = self.config['page']
        pageWidth = pageConfig['width'] + pageConfig['bleed']
        pageHeight = pageConfig['height']*2 + pageConfig['bleed']

        self.layerWidth = pageWidth
        self.layerHeight = pageConfig['height'] + pageConfig['bleed']/2

        image = gimp.Image(pageWidth,pageHeight, RGB)
        for [i, longPage] in enumerate(self.assembly):
            layer_group = pdb.gimp_layer_group_new(image)
            layer_group.name = 'page_%s' % (i+1)
            image.add_layer(layer_group, 0)
            if len(longPage) == 1:
                longPage.append({'name': 'skip' })
            for page in longPage:

                # select which folder to check for assets
                #+  build is for generated calendar and drawings for other ungenerated pages
                pagesFolderName = self.config['pagesFolderName']
                folder = "%s/../%s" % (os.path.dirname(os.path.abspath(__file__)), pagesFolderName)

                # calendrier name format is year-monthName-calendrier.xcf
                if re.match(r'.*calendrier$', page['name']):
                    folder = build
                    match = re.match(re.compile(ur'^(\w+)-précédent-(calendrier)', re.UNICODE), page['name'])
                    if match:
                        path = "%s/%s-%s-%s.xcf" % (folder, self.year-1, match.group(1), match.group(2))
                    else:
                        path = "%s/%s-%s.xcf" % (folder, self.year, page['name'])

                    found = [path] if os.path.exists(path) else []
                else:
                    # check for both extensions
                    path = "%s/%s" % (folder, page['name'])
                    found = [path + '.' + ext for ext in exts if (os.path.exists(path + '.' + ext))]

                if len(found) == 0:
                    # replace
                    print("no file found: ", page['name'])
                    page['file'] = drawings + "/" + FILE_NOT_FOUND
                    page['notFound'] = True
                else:
                    page['file'] = found[0]

            #print longPage
            self.createLongPage(image, layer_group, longPage)

        #scaledown to print on letter size
        #pdb.gimp_image_scale(image, 2550, 3300)
        #save file to ./build
        if self.assembled:
            filename = "assembly_printable.xcf"
        else:
            filename = "assembly_ordered.xcf"
        
        filenamepdf =  re.sub(r'xcf$', 'pdf', filename)
        path = '%s/%s' % (build, filename)
        pathpdf = '%s/%s' % (build, filenamepdf)
        pdb.gimp_xcf_save(0, image, image.layers[0], path, filename)
        layers_as_pages = 1
        
        
        pdb.file_pdf_save2(image, image.layers[0], pathpdf, filenamepdf, 0, 0, 0, layers_as_pages, 0)

        gimp.Display(image)
        print "Done!"

    def createLongPage(self, image, parent, longPage):
        top = longPage[0]
        bottom = longPage[1]

        def loadPage(page):
            print "file:", page['file']
            if re.match('.*xcf$', page['file']):

                return pdb.gimp_xcf_load(0, page['file'], page['name'])
            else:
                return pdb.file_png_load(page['file'], page['name'])

        for [i, obj] in enumerate([top, bottom]):
            loadedImage = loadPage(obj)

            if obj.has_key('notFound') and obj['notFound'] == True:
                layer = loadedImage.layers[0]
                txt = loadedImage.layers[0].layers[0]
                # used to display name of missing page; text is empty for release
                label = ''
                if self.config['displayNotFoundPageLabel'] == True:
                    label = obj['name']
                pdb.gimp_text_layer_set_text(txt, label)

                layer.name = obj['name']


            if obj.has_key('student'):
                watermark( self.config, loadedImage, obj)

            loadedImage.merge_visible_layers(CLIP_TO_IMAGE)
            layer = pdb.gimp_layer_new_from_drawable(loadedImage.layers[0], image)
            pdb.gimp_image_insert_layer(image, layer, parent, 0)
            pdb.gimp_layer_scale(layer, self.layerWidth, self.layerHeight, False)
            if obj.has_key('reverse') and obj['reverse']:
                pdb.gimp_item_transform_rotate_simple(layer, ROTATE_180, 1, 0, 0)
            if i == 1:
                pdb.gimp_layer_translate(layer, 0, self.layerHeight)
        pdb.gimp_image_merge_layer_group(image, parent)



def assemble(date_year, assembled):
    config = util.openPagesYaml()
    config['assembled'] = assembled
    config['year'] = date_year
    paginator = Paginator(config)
    paginator.assemble()



register(
  "python-fu-calendar-assy",
  'Calendar assembler',
  'assemble calendar based on Pages.yaml',
  "Mathieu Gagnon",
  "UNLICENCED",
  "2022",
  "assemble Calendar",
  "",
  [
    (PF_INT, "date_year", "Year", 2024),
    (PF_TOGGLE, "assembled", "assembled for printing (else ascending)", True),
  ],
  [],
  assemble,
  menu="<Image>/cal"
  )
