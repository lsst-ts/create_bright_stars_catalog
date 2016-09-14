import numpy as np
from lsst.sims.utils import ObservationMetaData, raDecFromPupilCoords
from lsst.sims.utils import haversine, arcsecFromRadians, distanceToSun
from lsst.sims.utils import altAzPaFromRaDec, _lonLatFromNativeLonLat
from lsst.sims.utils import sphericalFromCartesian, cartesianFromSpherical
from lsst.sims.utils import _observedFromICRS, _icrsFromObserved

import warnings

warnings.filterwarnings("ignore")

def fovCorners(obs, side_length):
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



def distance_in_arcminutes(ra1, dec1, ra2, dec2):
    """
    all ra and dec are in degrees
    """

    dd = haversine(np.radians(ra1), np.radians(dec1),
                   np.radians(ra2), np.radians(dec2))

    return arcsecFromRadians(dd)/60.0


if __name__ == "__main__":

    rng = np.random.RandomState(61)
    ra_list = rng.random_sample(50)*360.0
    dec_list = rng.random_sample(50)*180.0-90.0
    rot_list = rng.random_sample(50)*360.0
    mjd_list = rng.random_sample(50)*10000.0 + 59580.0

    for ra, dec, rot, mjd in zip(ra_list, dec_list, rot_list,mjd_list):

        obs = ObservationMetaData(pointingRA=ra, pointingDec=dec,
                                  rotSkyPos=rot, mjd=mjd)

        alt, az, pa = altAzPaFromRaDec(ra, dec, obs)

        ra_corner, dec_corner = fovCorners(obs, side_length=20.0)

        max_orthogonal = -1.0

        for ix1, ix2 in zip((0, 0, 1, 2), (1, 3, 2, 3)):
            dd = distance_in_arcminutes(ra_corner[ix1], dec_corner[ix1],
                                        ra_corner[ix2], dec_corner[ix2])

            if np.abs(dd-20.0)>max_orthogonal:
                max_orthogonal=np.abs(dd-20.0)

        dd = distance_in_arcminutes(ra_corner[2], dec_corner[2],
                                    ra_corner[0], dec_corner[0])

        d_sun = distanceToSun(ra, dec, obs.mjd.TDB)
        print 'max orthogonal errr ',max_orthogonal,ra,dec,rot,d_sun,alt
