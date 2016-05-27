import BrightStarDatabase
import FieldDatabase
import CameraData
import SkyCoverageSurvey

from lsst.sims.utils import ObservationMetaData

brightStarDatabaseHost = "140.252.32.27"
brightStarDatabasePort = 3306
brightStarDatabaseUser = "lsstwasadmin"
brightStarDatabasePassword = "lsstwasadmin"
brightStarDatabaseDatabase = "BrightStarCatalog"

fieldDatabaseFile = ".\Fields.txt"
fieldDatabaseAcceptableRADecl = lambda x: x[1] <= 2 or (x[0] >= 0 and x[0] <= 12 and x[1] <= 30)

cameraRotation = 32.0
cameraMJD = 59580.0
cameraFilter = BrightStarDatabase.FilterU

try:
    # Setup databases, simulations
    brightStarDatabase = BrightStarDatabase.BrightStarDatabase()
    fieldDatabase = FieldDatabase.FieldDatabase(".\Fields.txt", fieldDatabaseAcceptableRADecl)
    camera = CameraData.CameraData()
    survey = SkyCoverageSurvey.SkyCoverageSurvey()
    
    # Connect to database
    brightStarDatabase.connect(brightStarDatabaseHost, brightStarDatabasePort, brightStarDatabaseUser, brightStarDatabasePassword, brightStarDatabaseDatabase)

    # Get observation fields
    fieldRA, fieldDecl = fieldDatabase.getRADecl()
    for index in range(len(fieldRA)):
        # Get corners of wavefront sensors for this observation field
        obs = ObservationMetaData(pointingRA=fieldRA[index], pointingDec=fieldDecl[index], rotSkyPos=cameraRotation, mjd=cameraMJD)
        wavefrontSensors = camera.getWavefrontCorners(obs)
        for wavefrontSensor in wavefrontSensors:
            # Get stars in this wavefront sensor for this observation field
            stars = brightStarDatabase.query(cameraFilter, wavefrontSensor[0], wavefrontSensor[1], wavefrontSensor[2], wavefrontSensor[3])
            stars.populateDetector(wavefrontSensor)

finally:
    # Clean up
    brightStarDatabase.disconnect()