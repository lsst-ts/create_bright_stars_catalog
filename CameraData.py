import numpy as np

from lsst.sims.utils import ObservationMetaData, raDecFromPupilCoords
from lsst.sims.coordUtils.CameraUtils import raDecFromPixelCoords, _pupilCoordsFromRaDec, pixelCoordsFromRaDec
from lsst.sims.utils import ObservationMetaData, raDecFromPupilCoords
from lsst.sims.utils import haversine, arcsecFromRadians, distanceToSun
from lsst.sims.utils import altAzPaFromRaDec, _lonLatFromNativeLonLat
from lsst.sims.utils import sphericalFromCartesian, cartesianFromSpherical
from lsst.sims.utils import _observedFromICRS, _icrsFromObserved

import lsst.afw.geom as afwGeom
from lsst.afw.cameraGeom import PUPIL, PIXELS, TAN_PIXELS, FOCAL_PLANE
from lsst.afw.cameraGeom import WAVEFRONT

# instantiate the LSST camera model
from lsst.obs.lsstSim import LsstSimMapper

import warnings

warnings.filterwarnings("ignore")

class CameraData(object):
    def __init__(self):
        self.__camera = LsstSimMapper().camera
        self.__wavefrontDetectors = [] # this will be a list of the actual detectors
        self.__wavefrontCorners = [] # this will be a list of the x, y coordinates of the detectors' corners
        self.initializeWavefrontDetectors()
                                           
    def initializeWavefrontDetectors(self):
        """
        Initializes the camera wave front detectors.
        """
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
        """
        Populates the RAInPixel and DeclInPixel coordinates in the StarData stars using the lsst-sims stack.
        
        @param stars [in/out] The stars to populate.
        
        @param obs [in] The observation meta data (found in the lsst-sims stack) that defines the pointing.
        """
        ra = stars.RA
        decl = stars.Decl
        raInPixel, declInPixel = pixelCoordsFromRaDec(
            ra = ra, 
            dec = decl, 
            obs_metadata = obs,
            epoch = 2000.0,
            chipNames = np.array([stars.Detector] * len(stars.RA)),
            camera = self.__camera, 
           includeDistortion = True)
        stars.populateRAData(raInPixel)
        stars.populateDeclData(declInPixel)
        return
        
    def removeStarsNotOnDetector(self, stars, obs):
        """
        Removes the stars from the StarData stars that are not on the detector.
                
        @param stars [in/out] The input set of stars.
        
        @param obs [in] The observation meta data (found in the lsst-sims stack) that defines the pointing.
        """
        detectors = self.wavefrontFromRaDec(stars.RA, stars.Decl, obs)
        keep = [index for index in range(len(stars.RA)) if detectors[index] == stars.Detector]
        stars.RA = [stars.RA[index] for index in keep]
        stars.RAInPixel = [stars.RAInPixel[index] for index in keep]
        stars.RAInMM = [stars.RAInMM[index] for index in keep]
        stars.Decl = [stars.Decl[index] for index in keep]
        stars.DeclInPixel = [stars.DeclInPixel[index] for index in keep]
        stars.DeclInMM = [stars.DeclInMM[index] for index in keep]
        stars.ObsMagU = [stars.ObsMagU[index] for index in keep]
        stars.ObsMagUNew = [stars.ObsMagUNew[index] for index in keep]
        stars.LSSTMagU = [stars.LSSTMagU[index] for index in keep]
        stars.LSSTMagUNoATM = [stars.LSSTMagUNoATM[index] for index in keep]
        stars.ObsMagG = [stars.ObsMagG[index] for index in keep]
        stars.ObsMagGNew = [stars.ObsMagGNew[index] for index in keep]
        stars.LSSTMagG = [stars.LSSTMagG[index] for index in keep]
        stars.LSSTMagGNoATM = [stars.LSSTMagGNoATM[index] for index in keep]
        stars.ObsMagR = [stars.ObsMagR[index] for index in keep]
        stars.ObsMagRNew = [stars.ObsMagRNew[index] for index in keep]
        stars.LSSTMagR = [stars.LSSTMagR[index] for index in keep]
        stars.LSSTMagRNoATM = [stars.LSSTMagRNoATM[index] for index in keep]
        stars.ObsMagI = [stars.ObsMagI[index] for index in keep]
        stars.ObsMagINew = [stars.ObsMagINew[index] for index in keep]
        stars.LSSTMagI = [stars.LSSTMagI[index] for index in keep]
        stars.LSSTMagINoATM = [stars.LSSTMagINoATM[index] for index in keep]
        stars.ObsMagZ = [stars.ObsMagZ[index] for index in keep]
        stars.ObsMagZNew = [stars.ObsMagZNew[index] for index in keep]
        stars.LSSTMagZ = [stars.LSSTMagZ[index] for index in keep]
        stars.LSSTMagZNoATM = [stars.LSSTMagZNoATM[index] for index in keep]
        stars.ObsMagY = [stars.ObsMagY[index] for index in keep]
        stars.ObsMagYNew = [stars.ObsMagYNew[index] for index in keep]
        stars.LSSTMagY = [stars.LSSTMagY[index] for index in keep]
        stars.LSSTMagYNoATM = [stars.LSSTMagYNoATM[index] for index in keep]
        
        return
        
    def removeStarsNotOnDetectorSimple(self, stars, obs):
        """
        Removes the stars from the StarData stars that are not on the detector using pixel data.
                
        @param stars [in/out] The input set of stars.
        
        @param obs [in] The observation meta data (found in the lsst-sims stack) that defines the pointing.
        """
        keep = [index for index in range(len(stars.RA)) if stars.RAInPixel[index] >= 0 and stars.RAInPixel[index] <= 4096 and stars.DeclInPixel[index] >= 0 and stars.DeclInPixel[index] <= 2048]
        stars.RA = [stars.RA[index] for index in keep]
        stars.RAInPixel = [stars.RAInPixel[index] for index in keep]
        stars.RAInMM = [stars.RAInMM[index] for index in keep]
        stars.Decl = [stars.Decl[index] for index in keep]
        stars.DeclInPixel = [stars.DeclInPixel[index] for index in keep]
        stars.DeclInMM = [stars.DeclInMM[index] for index in keep]
        stars.ObsMagU = [stars.ObsMagU[index] for index in keep]
        stars.ObsMagUNew = [stars.ObsMagUNew[index] for index in keep]
        stars.LSSTMagU = [stars.LSSTMagU[index] for index in keep]
        stars.LSSTMagUNoATM = [stars.LSSTMagUNoATM[index] for index in keep]
        stars.ObsMagG = [stars.ObsMagG[index] for index in keep]
        stars.ObsMagGNew = [stars.ObsMagGNew[index] for index in keep]
        stars.LSSTMagG = [stars.LSSTMagG[index] for index in keep]
        stars.LSSTMagGNoATM = [stars.LSSTMagGNoATM[index] for index in keep]
        stars.ObsMagR = [stars.ObsMagR[index] for index in keep]
        stars.ObsMagRNew = [stars.ObsMagRNew[index] for index in keep]
        stars.LSSTMagR = [stars.LSSTMagR[index] for index in keep]
        stars.LSSTMagRNoATM = [stars.LSSTMagRNoATM[index] for index in keep]
        stars.ObsMagI = [stars.ObsMagI[index] for index in keep]
        stars.ObsMagINew = [stars.ObsMagINew[index] for index in keep]
        stars.LSSTMagI = [stars.LSSTMagI[index] for index in keep]
        stars.LSSTMagINoATM = [stars.LSSTMagINoATM[index] for index in keep]
        stars.ObsMagZ = [stars.ObsMagZ[index] for index in keep]
        stars.ObsMagZNew = [stars.ObsMagZNew[index] for index in keep]
        stars.LSSTMagZ = [stars.LSSTMagZ[index] for index in keep]
        stars.LSSTMagZNoATM = [stars.LSSTMagZNoATM[index] for index in keep]
        stars.ObsMagY = [stars.ObsMagY[index] for index in keep]
        stars.ObsMagYNew = [stars.ObsMagYNew[index] for index in keep]
        stars.LSSTMagY = [stars.LSSTMagY[index] for index in keep]
        stars.LSSTMagYNoATM = [stars.LSSTMagYNoATM[index] for index in keep]
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
        
    def fovCorners(self, obs, side_length):
        """
        obs is an ObservationMetaData
        side_length in arcminutes
        """

        # find the center of the field of view and convert it into "Observed RA, Dec"
        pointing_lon, pointing_lat = _observedFromICRS(np.array([obs._pointingRA]),
                                                       np.array([obs._pointingDec]),
                                                       obs_metadata=obs, epoch=2000.0)

        # figure out the length of the diagonal of your square field of view
        hypotenuse = np.sqrt(2.0*(side_length/60.0)**2)
        half_length = np.radians(0.5*hypotenuse)

        # Create a fiducial field of view cetnered on the north pole.
        # We will take this field of viewand rotate it so that it has
        # the correct orientation, then translate it down the celestial
        # sphere to the actual position of your telescope pointing.
        native_lon_list = np.array([0.0, np.pi/2.0, np.pi, 1.5*np.pi])
        native_lat_list = np.array([0.5*np.pi-half_length]*4)


        # rotate your field of view to account for the rotation of the sky

        rot_angle = -1.0*obs._rotSkyPos+0.25*np.pi  # the extra 0.25 pi is to align our field
                                                    # of view so that rotSkyPos=0 puts the
                                                    # northern edge vertically up (when we
                                                    # created the field of view, one of the
                                                    # corners was vertically up)
        cosRot = np.cos(rot_angle)
        sinRot = np.sin(rot_angle)

        rotz = np.array([[cosRot, sinRot, 0.0],[-sinRot, cosRot, 0.0], [0.0, 0.0, 1.0]])

        xyz = cartesianFromSpherical(native_lon_list, native_lat_list)

        rot_xyz = []

        for vec in xyz:
            new_xyz = np.dot(rotz, vec)
            rot_xyz.append(new_xyz)

        rot_xyz = np.array(rot_xyz)

        rot_lon, rot_lat = sphericalFromCartesian(rot_xyz)

        # translate the field of view down to the actual telescope pointing
        ra_obs, dec_obs = _lonLatFromNativeLonLat(rot_lon, rot_lat,
                                                  pointing_lon[0], pointing_lat[0])

        return np.degrees(_icrsFromObserved(ra_obs, dec_obs, obs_metadata=obs, epoch=2000.0))



    def distance_in_arcminutes(self, ra1, dec1, ra2, dec2):
        """
        all ra and dec are in degrees
        """

        dd = haversine(np.radians(ra1), np.radians(dec1),
                       np.radians(ra2), np.radians(dec2))

        return arcsecFromRadians(dd)/60.0

if __name__ == "__main__":
    start = 30
    stop = -90
    degrees = abs(stop - start) 
    minutesPerDegree = 5
    secondsPerMinute = 1
    scale = 1
    number = degrees * minutesPerDegree * secondsPerMinute * scale
    data = np.linspace(start, stop, num = number)
    dataLen = len(data)
    summaryFilePath = "foobar.csv"
    print dataLen
    map = {
        "R:0,0 S:2,2,A" : 0,
        "R:0,0 S:2,2,B" : 1,
        "R:0,4 S:2,0,A" : 2,
        "R:0,4 S:2,0,B" : 3,
        "R:4,0 S:0,2,A" : 4,
        "R:4,0 S:0,2,B" : 5,
        "R:4,4 S:0,0,A" : 6,
        "R:4,4 S:0,0,B" : 7}

    camera = CameraData()
    summaryFile = open(summaryFilePath, "w+")
    summaryFile.write("PointingRA,PointingDec,")
    for i in range(8):
        for j in range(4):
            summaryFile.write("%d-%dRA,%d-%dDec," % (i, j, i, j))
    summaryFile.write("\r\n")
    count = 0
    for item in data:
        count += 1
        print "%d of %d" % (count, dataLen)
        obs = ObservationMetaData(pointingRA=0, pointingDec=item, rotSkyPos=32.0, mjd=59580.0)
        wavefrontSensors = camera.getWavefrontCorners(obs)
        line = ""
        for key in map:
            wavefrontSensor = wavefrontSensors[key]
            line = line + "%f,%f,%f,%f,%f,%f,%f,%f" % (wavefrontSensor[0][0], wavefrontSensor[0][1], wavefrontSensor[1][0], wavefrontSensor[1][1], wavefrontSensor[2][0], wavefrontSensor[2][1], wavefrontSensor[3][0], wavefrontSensor[3][1])
        summaryFile.write("%f,%f,%s\r\n" % (item, 0, line))