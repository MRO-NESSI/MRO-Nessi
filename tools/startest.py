#!/usr/bin/env python
"""This is a test program to determine the center of rotation for a star field.
This will be done by taking a series of images of a single star, offset from the
center of the field at different k-mirror angles.  Then, finding the centroids 
of the star in each image and using this data to determine the pixel coordinates
of the center of rotation.

Method taken from the Scipy cookbook:
http://www.scipy.org/Cookbook/Least_Squares_Circle
"""
import PyGuide

ccdInfo = PyGuide.CCDInfo(100.0, 12.5, 1.5, 65535)
# these are general settings
thresh = 5.0
radMult = 3.0
rad = 15
satLevel = (2**16)-1
verbosity = 2
doDS9 = False
mask = None
satMask = None

from numpy import *

# 2D coordinates of the desired star locations

xf = r_[  90, 350, -130,  100,  230,   0]
yf = r_[ 340, 100,   60, -140,  270, -100]

import pyfits
from PyGuide import FakeData
def Fakes():
    """generate sample images with single star located at (xf,yf) coordinates to
    simulate images taken at different k-mirror orientations."""
    #make fake star peak is 25,000, centered at (50,50) of a (100,100) array
    star = FakeData.fakeStar((100,100), (50,50), 2, 25000)
    #print star[45:55, 45:55]
    for i in range(len(xf)):
        # get fits HDU
        baseimHDU = pyfits.open('circleCentroid.fits')
        # get the header
        baseimHeader = baseimHDU[0].header
        print baseimHeader['BITPIX']
        # get the image data
        baseimData = baseimHDU[0].data
        
        # add star to image data
        baseimData[512+xf[i]-50:512+xf[i]+49, 512+yf[i]-50:512+yf[i]+49] = baseimData[512+xf[i]-50:512+xf[i]+49, 512+yf[i]-50:512+yf[i]+49] + star[0:99, 0:99]
        
        # save new image
        baseimHDU[0].scale('int16', '', bzero=32768)
        baseimHDU[0].writeto(str(i) + 'out.fits')
        print "Image ", str(i), "generated."

def FakeFringeSpot():
    """generate a fake image from the fringe camera, no mask."""
    #make fake star peak is 200, centered at (50,50) of a (100,100) array
    star = FakeData.fakeStar((100,100), (50,50), 25, 200)
    import Image, numpy
    
    im = Image.open('fringe-star.TIF')
    imarray = numpy.array(im)
    
    # add star to image data
    imarray[256-50:256+49, 256-50:256+49] = imarray[256-50:256+49, 256-50:256+49] + star[0:99, 0:99]
    
    # save new image
    newim = Image.fromarray(imarray)
    newim.save("fringe-spot.TIF", "TIFF")
    print "Image generated."

def CenterStar(filename, camera='GUIDE'):
    """Determine pixel location of a star that is supposed to be centered in the field
    of view, camera type selects between GUIDE camera and FRINGE camera."""
    if camera=='GUIDE':
        print 'Centroid GUIDE'
        hdu = pyfits.open(filename)
        data = hdu[0].data
        stars = PyGuide.findStars(data, mask, satMask, ccdInfo, thresh, radMult, rad, verbosity, doDS9)
        initialxy = stars[0][0].xyCtr
        centroid = PyGuide.Centroid.centroid(data, mask, satMask, initialxy, rad, ccdInfo)
        #put centroids into x,y
        xy = centroid.xyCtr
        print xy
        
    if camera=='FRINGE':
        import Image, numpy
        rad = 150
        ccdInfo = PyGuide.CCDInfo(2.0, 1.5, 1.5, 256)
        
        im = Image.open(filename)
        imarray = numpy.array(im)
        stars = PyGuide.findStars(imarray, mask, satMask, ccdInfo, thresh, radMult, rad, verbosity, doDS9)
        initialxy = stars[0][0].xyCtr
        centroid = PyGuide.Centroid.centroid(imarray, mask, satMask, initialxy, rad, ccdInfo)
        #put centroids into x,y
        xy = centroid.xyCtr
        print xy
        im.show()
        print 'Centroid FRINGE'

def FindCircle(numfiles):
    """Fit a circle to the centroids of a star image at different k-mirror orientations."""
    centroids = []
    names = []
    hdus = []
    data = []
    x = r_[0.0]
    y = r_[0.0]
    for i in range(numfiles-1):
        x = append(x, 0.0)
        y = append(y, 0.0)
    #open series of files
    for i in range(numfiles):
        names.append(str(i)+'out.fits')
        hdus.append(str(i)+'hdu')
        data.append(str(i)+'data')
        
    
    print names, hdus, data      
    #find centroids
    j=0
    for imgs in names:
        imHDU = pyfits.open(imgs)
        imData = imHDU[0].data
        stars = PyGuide.findStars(imData, mask, satMask, ccdInfo, thresh, radMult, rad, verbosity, doDS9)
        initialxy = stars[0][0].xyCtr
        centroid = PyGuide.Centroid.centroid(imData, mask, satMask, initialxy, rad, ccdInfo)
        #put centroids into x,y
        xy = centroid.xyCtr
        x[j] = xy[0]
        y[j] = xy[1]
        j+=1
        
    print x
    print y
    #find circle

    basename = 'circle'

    
    # basename = 'arc'

    # # Code to generate random data points
    # R0 = 25
    # nb_pts = 40
    # dR = 1
    # angle =10*pi/5
    # theta0 = random.uniform(0, angle, size=nb_pts)
    # x = (10 + R0*cos(theta0) + dR*random.normal(size=nb_pts)).round()
    # y = (10 + R0*sin(theta0) + dR*random.normal(size=nb_pts)).round()


    # == METHOD 1 ==
    method_1 = 'algebraic'

    # coordinates of the barycenter
    x_m = mean(x)
    y_m = mean(y)

    # calculation of the reduced coordinates
    u = x - x_m
    v = y - y_m

    # linear system defining the center in reduced coordinates (uc, vc):
    #    Suu * uc +  Suv * vc = (Suuu + Suvv)/2
    #    Suv * uc +  Svv * vc = (Suuv + Svvv)/2
    Suv  = sum(u*v)
    Suu  = sum(u**2)
    Svv  = sum(v**2)
    Suuv = sum(u**2 * v)
    Suvv = sum(u * v**2)
    Suuu = sum(u**3)
    Svvv = sum(v**3)

    # Solving the linear system
    A = array([ [ Suu, Suv ], [Suv, Svv]])
    B = array([ Suuu + Suvv, Svvv + Suuv ])/2.0
    uc, vc = linalg.solve(A, B)

    xc_1 = x_m + uc
    yc_1 = y_m + vc

    # Calculation of all distances from the center (xc_1, yc_1)
    Ri_1      = sqrt((x-xc_1)**2 + (y-yc_1)**2)
    R_1       = mean(Ri_1)
    residu_1  = sum((Ri_1-R_1)**2)
    residu2_1 = sum((Ri_1**2-R_1**2)**2)

    # Decorator to count functions calls
    import functools
    def countcalls(fn):
        "decorator function count function calls "

        @functools.wraps(fn)
        def wrapped(*args):
            wrapped.ncalls +=1
            return fn(*args)

        wrapped.ncalls = 0
        return wrapped

    #  == METHOD 2 ==
    # Basic usage of optimize.leastsq
    from scipy      import optimize

    method_2  = "leastsq"

    def calc_R(xc, yc):
        """ calculate the distance of each 2D points from the center (xc, yc) """
        return sqrt((x-xc)**2 + (y-yc)**2)

    @countcalls
    def f_2(c):
        """ calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) """
        Ri = calc_R(*c)
        return Ri - Ri.mean()

    center_estimate = x_m, y_m
    center_2, ier = optimize.leastsq(f_2, center_estimate)

    xc_2, yc_2 = center_2
    Ri_2       = calc_R(xc_2, yc_2)
    R_2        = Ri_2.mean()
    residu_2   = sum((Ri_2 - R_2)**2)
    residu2_2  = sum((Ri_2**2-R_2**2)**2)
    ncalls_2   = f_2.ncalls

    # == METHOD 2b ==
    # Advanced usage, with jacobian
    method_2b  = "leastsq with jacobian"

    def calc_R(xc, yc):
        """ calculate the distance of each 2D points from the center c=(xc, yc) """
        return sqrt((x-xc)**2 + (y-yc)**2)

    @countcalls
    def f_2b(c):
        """ calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) """
        Ri = calc_R(*c)
        return Ri - Ri.mean()

    @countcalls
    def Df_2b(c):
        """ Jacobian of f_2b
        The axis corresponding to derivatives must be coherent with the col_deriv option of leastsq"""
        xc, yc     = c
        df2b_dc    = empty((len(c), x.size))

        Ri = calc_R(xc, yc)
        df2b_dc[ 0] = (xc - x)/Ri                   # dR/dxc
        df2b_dc[ 1] = (yc - y)/Ri                   # dR/dyc
        df2b_dc       = df2b_dc - df2b_dc.mean(axis=1)[:, newaxis]

        return df2b_dc

    center_estimate = x_m, y_m
    center_2b, ier = optimize.leastsq(f_2b, center_estimate, Dfun=Df_2b, col_deriv=True)

    xc_2b, yc_2b = center_2b
    Ri_2b        = calc_R(xc_2b, yc_2b)
    R_2b         = Ri_2b.mean()
    residu_2b    = sum((Ri_2b - R_2b)**2)
    residu2_2b   = sum((Ri_2b**2-R_2b**2)**2)
    ncalls_2b    = f_2b.ncalls

    print """
    Method 2b :
    print "Functions calls : f_2b=%d Df_2b=%d""" % ( f_2b.ncalls, Df_2b.ncalls)



    # Summary
    fmt = '%-22s %10.5f %10.5f %10.5f %10d %10.6f %10.6f %10.2f'
    print ('\n%-22s' +' %10s'*7) % tuple('METHOD Xc Yc Rc nb_calls std(Ri) residu residu2'.split())
    print '-'*(22 +7*(10+1))
    print  fmt % (method_1 , xc_1 , yc_1 , R_1 ,        1 , Ri_1.std() , residu_1 , residu2_1 )
    print  fmt % (method_2 , xc_2 , yc_2 , R_2 , ncalls_2 , Ri_2.std() , residu_2 , residu2_2 )

    # plotting functions
    from matplotlib                 import pyplot as p, cm, colors
    p.close('all')

    def plot_all(residu2=False):
        """ Draw data points, best fit circles and center for the three methods,
        and adds the iso contours corresponding to the fiel residu or residu2
        """

        f = p.figure( facecolor='white')  #figsize=(7, 5.4), dpi=72,
        p.axis('equal')

        theta_fit = linspace(-pi, pi, 180)

        x_fit1 = xc_1 + R_1*cos(theta_fit)
        y_fit1 = yc_1 + R_1*sin(theta_fit)
        p.plot(x_fit1, y_fit1, 'b-' , label=method_1, lw=2)

        x_fit2 = xc_2 + R_2*cos(theta_fit)
        y_fit2 = yc_2 + R_2*sin(theta_fit)
        p.plot(x_fit2, y_fit2, 'k--', label=method_2, lw=2)

        p.plot([xc_1], [yc_1], 'bD', mec='y', mew=1)
        p.plot([xc_2], [yc_2], 'gD', mec='r', mew=1)
     
        # draw
        p.xlabel('x')
        p.ylabel('y')

        # plot the residu fields
        nb_pts = 100

        p.draw()
        xmin, xmax = p.xlim()
        ymin, ymax = p.ylim()

        vmin = min(xmin, ymin)
        vmax = max(xmax, ymax)

        xg, yg = ogrid[vmin:vmax:nb_pts*1j, vmin:vmax:nb_pts*1j]
        xg = xg[..., newaxis]
        yg = yg[..., newaxis]

        Rig    = sqrt( (xg - x)**2 + (yg - y)**2 )
        Rig_m  = Rig.mean(axis=2)[..., newaxis]

        if residu2 : residu = sum( (Rig**2 - Rig_m**2)**2 ,axis=2)
        else       : residu = sum( (Rig-Rig_m)**2 ,axis=2)

        lvl = exp(linspace(log(residu.min()), log(residu.max()), 15))

        p.contourf(xg.flat, yg.flat, residu.T, lvl, alpha=0.4, cmap=cm.Purples_r) # , norm=colors.LogNorm())
        cbar = p.colorbar(fraction=0.175, format='%.f')
        p.contour (xg.flat, yg.flat, residu.T, lvl, alpha=0.8, colors="lightblue")

        if residu2 : cbar.set_label('Residu_2 - algebraic approximation')
        else       : cbar.set_label('Residu')

        # plot data
        p.plot(x, y, 'ro', label='data', ms=8, mec='b', mew=1)
        p.legend(loc='best',labelspacing=0.1 )

        p.xlim(xmin=vmin, xmax=vmax)
        p.ylim(ymin=vmin, ymax=vmax)

        p.grid()
        p.title('Least Squares Circle')
        p.savefig('%s_residu%d.png' % (basename, 2 if residu2 else 1))

    plot_all(residu2=False)
    plot_all(residu2=True )

    p.show()