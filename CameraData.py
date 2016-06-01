import numpy as np

from lsst.sims.utils import ObservationMetaData
from lsst.sims.coordUtils.CameraUtils import raDecFromPixelCoords, _pupilCoordsFromRaDec, pixelCoordsFromRaDec

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
        raInPixel, declInPixel = pixelCoordsFromRaDec(
            ra = ra, 
            dec = decl, 
            obs_metadata = obs,
            epoch = 2000.0,
            chipNames = np.array([stars.Detector] * len(stars.ID)),
            camera = self.__camera, 
           includeDistortion = True)
        stars.populateRAData(raInPixel)
        stars.populateDeclData(declInPixel)
        return stars
        
    def removeStarsNotOnDetector(self, stars, obs):
        detectors = self.wavefrontFromRaDec(stars.RA, stars.Decl, obs)
        keep = [index for index in range(len(stars.ID)) if detectors[index] == stars.Detector]
        stars.ID = [stars.ID[index] for index in keep]
        stars.RA = [stars.RA[index] for index in keep]
        stars.Decl = [stars.Decl[index] for index in keep]
        stars.Mag = [stars.Mag[index] for index in keep]
        return
        
    def _wavefrontFromPupilCoords(self, xPupil, yPupil, camera=None, allow_multiple_chips=False):
        """
        Return the names of detectors that see the object specified by
        either (xPupil, yPupil).  Note: this method does not return
        the name of guide, focus, or wavefront detectors.

        @param [in] xPupil a numpy array of x pupil coordinates in radians

        @param [in] yPupil a numpy array of y pupil coordinates in radians

        @param [in] allow_multiple_chips is a boolean (default False) indicating whether or not
        this method will allow objects to be visible on more than one chip.  If it is 'False'
        and an object appears on more than one chip, an exception will be raised.  If it is 'True'
        and an object falls on more than one chip, it will still only return the first chip in the
        list of chips returned. THIS BEHAVIOR SHOULD BE FIXED IN A FUTURE TICKET.

        @param [in] camera is an afwCameraGeom object that specifies the attributes of the camera.

        @param [out] a numpy array of chip names (science detectors only)

        """

        if not isinstance(xPupil, np.ndarray) or not isinstance(yPupil, np.ndarray):
            raise RuntimeError("You need to pass numpy arrays of xPupil and yPupil to chipNameFromPupilCoords")

        if len(xPupil) != len(yPupil):
            raise RuntimeError("You passed %d xPupils and %d yPupils " % (len(xPupil), len(yPupil)) +
                               "to chipName.")

        if camera is None:
            raise RuntimeError("No camera defined.  Cannot run chipName.")

        chipNames = []

        cameraPointList = [afwGeom.Point2D(x,y) for x,y in zip(xPupil, yPupil)]

        detList = self.__camera.findDetectorsList(cameraPointList, PUPIL)

        for pt, det in zip(cameraPointList, detList):
            if len(det)==0 or np.isnan(pt.getX()) or np.isnan(pt.getY()):
                chipNames.append(None)
            else:
                names = [dd.getName() for dd in det]
                if len(names)>1 and not allow_multiple_chips:
                    raise RuntimeError("This method does not know how to deal with cameras " +
                                       "where points can be on multiple detectors.  " +
                                       "Override CameraCoords.get_chipName to add this.")
                elif len(names)==0:
                    chipNames.append(None)
                else:
                    chipNames.append(names[0])

        return np.array(chipNames)


    def wavefrontFromRaDec(self, ra_in, dec_in, obs_metadata=None):
        """
        Return the names of science detectors that see the object specified by
        (ra, Dec).

        @param [in] ra_in in degrees (a numpy array).
        In the International Celestial Reference System.

        @param [in] dec_in in degrees (a numpy array).
        In the International Celestial Reference System.

        @param [in] obs_metadata is an ObservationMetaData characterizing the telescope pointing

        @param [out] a numpy array of chip names
        """

        ra = np.radians(ra_in)
        dec = np.radians(dec_in)
        allow_multiple_chips=False
        epoch=2000.0
        camera=self.__camera

        if not isinstance(ra, np.ndarray) or not isinstance(dec, np.ndarray):
            raise RuntimeError("You need to pass numpy arrays of RA and Dec to chipName")

        if len(ra) != len(dec):
            raise RuntimeError("You passed %d RAs and %d Decs " % (len(ra), len(dec)) +
                               "to chipName.")

        if obs_metadata is None:
            raise RuntimeError("You need to pass an ObservationMetaData into chipName")

        if obs_metadata.mjd is None:
            raise RuntimeError("You need to pass an ObservationMetaData with an mjd into chipName")

        if obs_metadata.rotSkyPos is None:
            raise RuntimeError("You need to pass an ObservationMetaData with a rotSkyPos into chipName")

        xp, yp = _pupilCoordsFromRaDec(ra, dec, obs_metadata=obs_metadata, epoch=epoch)
        return self._wavefrontFromPupilCoords(xp, yp, camera=camera, allow_multiple_chips=allow_multiple_chips)

if __name__ == "__main__":
    # Specify a telescope pointing.
    # The convention for rotSkyPos can be seen by calling help(ObservationMetaData)
    # in an interactive python session.
    obs = ObservationMetaData(pointingRA=25.0, pointingDec=-12.0,
                              rotSkyPos=32.0, mjd=59580.0)
                              
    camera = CameraData()

    corners = camera.getWavefrontCorners(obs)
    print corners
    print "printing out the RA, Dec values of the corners of each wavefront sensor"
    for wavefront_name in corners:
        cc = corners[wavefront_name]
        print "%s (%.2f, %.2f) (%.2f, %.2f) (%.2f, %.2f) (%.2f, %.2f)" \
        %(wavefront_name, cc[0][0], cc[0][1], cc[1][0], cc[1][1],
        cc[2][0], cc[2][1], cc[3][0], cc[3][1])