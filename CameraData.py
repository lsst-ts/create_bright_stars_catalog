import numpy as np

from lsst.sims.utils import ObservationMetaData
from lsst.sims.coordUtils.CameraUtils import raDecFromPixelCoords, _pupilCoordsFromRaDec

import lsst.afw.geom as afwGeom
from lsst.afw.cameraGeom import PUPIL, PIXELS, TAN_PIXELS, FOCAL_PLANE
from lsst.afw.cameraGeom import WAVEFRONT

# instantiate the LSST camera model
from lsst.obs.lsstSim import LsstSimMapper

class CameraData(object):
    def __init__(self):
        self.__camera = LsstSimMapper().camera
        self.__wavefrontDetectors = [] # this will be a list of the actual detectors
        self.__wavefrontCorners = [] # this will be a list of the x, y coordinates of the detectors' corners
        self.initializeWavefrontDetectors()
                                           
    def initializeWavefrontDetectors(self):
        for detector in self.__camera:
                if detector.getType() == WAVEFRONT:
                    self.__wavefrontDetectors.append(detector)

                    bbox = detector.getBBox()
                    xmin = bbox.getMinX()
                    xmax = bbox.getMaxX()
                    ymin = bbox.getMinY()
                    ymax = bbox.getMaxY()
                    self.__wavefrontCorners.append((np.array([xmin, xmin, xmax, xmax]), np.array([ymin, ymax, ymin, ymax])))


    def getWavefrontCorners(self, obs):
        """
        Input
        ----------
        obs is an instantiation of ObservationMetaData that describes the pointing
        of the telescope

        Output
        ---------
        This method returns a dict of list.  The dict is keyed on the name of the
        wavefront sensor.  The list contains the (RA, Dec) coordinates of the corners
        of that sensor (RA, Dec are paired as tuples). For example

        output['R:0,0 S:2,2B'] = [(23.0, -5.0), (23.1, -5.0), (23.0, -5.1), (23.1, -5.1)]

        would mean that the wavefront sensor named 'R:0,0 S:2,2B' has its corners at
        RA 23, Dec -5; RA 23.1, Dec -5; RA 23, Dec -5.1; and RA 23.1, Dec -5.1

        Coordinates are in degrees.
        """
        ra_dec_out = {}

        for detector, coords in zip(self.__wavefrontDetectors, self.__wavefrontCorners):
            ra, dec = raDecFromPixelCoords(coords[0], coords[1], [detector.getName()]*len(coords[0]),
                                           camera=self.__camera, obs_metadata=obs,
                                           epoch=2000.0, includeDistortion=True)

            ra_dec_out[detector.getName()] = [(ra[0], dec[0]), (ra[1], dec[1]), (ra[2], dec[2]), (ra[3], dec[3])]

        return ra_dec_out
        
    def populatePixelFromRADecl(self, stars, obs):
        ra = stars.RA
        decl = stars.Decl
        raInPixel, declInPixel = pixelCoordsFromRaDec(ra, decl, camera = self.__camera, obs_metadata = obs,epoch = 2000.0, includeDistortion = True)
        stars.populateRAData(raInPixel)
        stars.populateDeclData(declInPixel)
        return stars
        

if __name__ == "__main__":

    # Specify a telescope pointing.
    # The convention for rotSkyPos can be seen by calling help(ObservationMetaData)
    # in an interactive python session.
    obs = ObservationMetaData(pointingRA=25.0, pointingDec=-12.0,
                              rotSkyPos=32.0, mjd=59580.0)

    corners = get_wavefront_corners(obs)
    print "printing out the RA, Dec values of the corners of each wavefront sensor"
    for wavefront_name in corners:
        cc = corners[wavefront_name]
        print "%s (%.2f, %.2f) (%.2f, %.2f) (%.2f, %.2f) (%.2f, %.2f)" \
        %(wavefront_name, cc[0][0], cc[0][1], cc[1][0], cc[1][1],
        cc[2][0], cc[2][1], cc[3][0], cc[3][1])


    print "\n"
    print "Identify the chips on which certain (RA, Dec) pairs fall"
    for wavefront_name in corners:
        cc = corners[wavefront_name]
        ra_min = min([cc[ix][0] for ix in range(4)])
        ra_max = max([cc[ix][0] for ix in range(4)])
        dec_min = min([cc[ix][1] for ix in range(4)])
        dec_max = max([cc[ix][1] for ix in range(4)])

        print "\ntry putting objects on ",wavefront_name

        for rr in np.arange(ra_min, ra_max, 0.333*(ra_max-ra_min)):
            for dd in np.arange(dec_min, dec_max, 0.333*(dec_max-dec_min)):

                chip_name = wavefrontFromRaDec(np.array([rr]), np.array([dd]), obs_metadata=obs)
                print "    ",chip_name