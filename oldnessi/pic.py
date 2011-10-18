#!/usr/bin/env python
"""This module holds all of the image manipulation functions."""

#image manipulation
import Image
import ImageEnhance
import ImageOps
import wx
import pyfits
import random
import numarray as num
import scipy.ndimage as nd
import pylab as py
import numpy as np

random.seed()

def getimg(image):
    testimg = pyfits.open(image)
    data = testimg[0].data
    img = Image.fromarray(data)
    #flip image vertically to deal with different origin definitions
    img = ImageOps.flip(img)
    return img

#generate test guide data, move image randomly by small amounts
def fakeit(f):
    py.clf()
    im = pyfits.open('test2.fits')
    data = im[0].data
    shiftx = random.randint(0, 10)
    shifty = random.randint(0, 10)
    shifted = nd.interpolation.shift(data, (shiftx, shifty))
    #py.figure(f)
    #py.imshow(np.log10(shifted), cmap=py.cm.Greys)
    #py.show()
    return shifted

def pic_cont_bri(img, cont, bri):
    imc = ImageEnhance.Contrast(img)
    imc_new = imc.enhance(cont)
    imb = ImageEnhance.Brightness(imc_new)
    imb_new = imb.enhance(bri)
    return imb_new
      
#overlay compass rose at specified angle
def compass(img, northang):
    xsize, ysize = img.size
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    #import compass and paste it on the image
    mark = Image.open('compass.png')
    rotmark = mark.rotate(northang) # deg counterclockwise - may need to check math/orientation on this
    layer.paste(rotmark, (xsize-100,ysize-100))
    # composite the watermark with the layer
    comp = Image.composite(layer, img, layer)
    comp.show()
    return comp


#Conversion between wx.Image wx.Bitmap and PIL Image from http://wiki.wxpython.org/WorkingWithImages

def WxBitmapToPilImage( myBitmap ) :
    return WxImageToPilImage( WxBitmapToWxImage( myBitmap ) )

def WxBitmapToWxImage( myBitmap ) :
    return wx.ImageFromBitmap( myBitmap )

def PilImageToWxBitmap( myPilImage ) :
    return WxImageToWxBitmap( PilImageToWxImage( myPilImage ) )

def PilImageToWxImage( myPilImage ):
    myWxImage = wx.EmptyImage( myPilImage.size[0], myPilImage.size[1] )
    myWxImage.SetData( myPilImage.convert( 'RGB' ).tostring() )
    return myWxImage

# Or, if you want to copy any alpha channel, too (available since wxPython 2.5)
# The source PIL image doesn't need to have alpha to use this routine.
# But, a PIL image with alpha is necessary to get a wx.Image with alpha.

def PilImageToWxImage( myPilImage, copyAlpha=True ) :

    hasAlpha = myPilImage.mode[ -1 ] == 'A'
    if copyAlpha and hasAlpha :  # Make sure there is an alpha layer copy.

        myWxImage = wx.EmptyImage( *myPilImage.size )
        myPilImageCopyRGBA = myPilImage.copy()
        myPilImageCopyRGB = myPilImageCopyRGBA.convert( 'RGB' )    # RGBA --> RGB
        myPilImageRgbData =myPilImageCopyRGB.tostring()
        myWxImage.SetData( myPilImageRgbData )
        myWxImage.SetAlphaData( myPilImageCopyRGBA.tostring()[3::4] )  # Create layer and insert alpha values.

    else :    # The resulting image will not have alpha.

        myWxImage = wx.EmptyImage( *myPilImage.size )
        myPilImageCopy = myPilImage.copy()
        myPilImageCopyRGB = myPilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
        myPilImageRgbData =myPilImageCopyRGB.tostring()
        myWxImage.SetData( myPilImageRgbData )

    return myWxImage

#-----

def imageToPil( myWxImage ):
    myPilImage = Image.new( 'RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()) )
    myPilImage.fromstring( myWxImage.GetData() )
    return myPilImage

def WxImageToWxBitmap( myWxImage ) :
    return myWxImage.ConvertToBitmap()
        