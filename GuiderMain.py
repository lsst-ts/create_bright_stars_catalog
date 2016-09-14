import BrightStarDatabase
import FieldDatabase
import CameraData
import SkyCoverageSurvey
import StarData
import time

from lsst.sims.utils import ObservationMetaData

brightStarDatabaseHost = "localhost:51433"
brightStarDatabaseUser = "LSST-2"
brightStarDatabasePassword = "L$$TUser"
brightStarDatabaseDatabase = "LSSTCATSIM"

fieldDatabaseFile = ".\Fields.txt"
fieldDatabaseAcceptableRADecl = lambda x: x[1] <= 85 and x[1] >= -85

cameraMJD = 59580.0
sideLength = 14             # Length of the FoV in arcmins

outputPath = ""

summaryFile = []

def getProperty(filter):
    if filter == BrightStarDatabase.FilterU:
        return lambda x: x.LSSTMagU
    elif filter == BrightStarDatabase.FilterG:
        return lambda x: x.LSSTMagG
    elif filter == BrightStarDatabase.FilterR:
        return lambda x: x.LSSTMagR
    elif filter == BrightStarDatabase.FilterI:
        return lambda x: x.LSSTMagI
    elif filter == BrightStarDatabase.FilterZ:
        return lambda x: x.LSSTMagZ
    else:
        return lambda x: x.LSSTMagY

def runSurvey(cameraFilters, cameraRotations, lowMagnitudes, highMagnitudes, summaryFilePath):
    try:
        for testIndex in range(len(lowMagnitudes)):
            cameraFilter = cameraFilters[testIndex]
            cameraRotation = cameraRotations[testIndex]
            lowMagnitude = lowMagnitudes[testIndex]
            highMagnitude = highMagnitudes[testIndex]
            
            # Create summary file
            # The summary file will contain high level information about each field
            # It can be used to see total counts of stars but no detail about each star
            summaryFile.append(open(summaryFilePath % (cameraFilter), "w+"))
            summaryFile[testIndex].write("Camera Rotation,%f,,,\r\n" % cameraRotation)
            summaryFile[testIndex].write("Camera Filter,%s,,,\r\n" % cameraFilter)
            summaryFile[testIndex].write("Low Magnitude,%f,,,\r\n" % lowMagnitude)
            summaryFile[testIndex].write("High Magnitude,%f,,,\r\n" % highMagnitude)
            summaryFile[testIndex].write("Side Length,%f,,,\r\n" % sideLength)
            summaryFile[testIndex].write("%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Stars Queried", "Stars Matching Criteria"))

        # Setup databases, simulations, and survey
        brightStarDatabase = BrightStarDatabase.BrightStarDatabase()
        fieldDatabase = FieldDatabase.FieldDatabase("Fields.txt", fieldDatabaseAcceptableRADecl)
        camera = CameraData.CameraData()
        
        # Connect to database
        brightStarDatabase.connect(brightStarDatabaseHost, brightStarDatabaseUser, brightStarDatabasePassword, brightStarDatabaseDatabase)
     
        # Get observation fields
        fieldRA, fieldDecl = fieldDatabase.getRADecl()
        for index in range(len(fieldRA)):
            print "Field #%d of %d" % ((index + 1), len(fieldRA))
            
            # Get corners of wavefront sensors for this observation field
            obs = ObservationMetaData(pointingRA=fieldRA[index], pointingDec=fieldDecl[index], rotSkyPos=cameraRotation, mjd=cameraMJD)
            raCorner, declCorner = camera.fovCorners(obs, sideLength)

            # Get stars in this FoV for this observation field
            stars = brightStarDatabase.query([raCorner[0], declCorner[0]], [raCorner[1], declCorner[1]], [raCorner[2], declCorner[2]], [raCorner[3], declCorner[3]])
            starsQueried = len(stars.RA)
            print "\t\tStars queried %d" % starsQueried
            
            # Get stars matching criteria
            starsMatchingCriteria = 0
            propertyLambda = getProperty(cameraFilter)
            for starIndex in range(len(stars.RA)):
                starMagnitude = propertyLambda(stars)[starIndex]
                
                if starMagnitude >= lowMagnitude and starMagnitude <= highMagnitude:
                    starsMatchingCriteria += 1
            print "\t\tStars matching criteria %d" % starsMatchingCriteria
             
            # Log summary results
            currentTime = time.time()
            summaryFile[testIndex].write("%f,%d,%f,%f,%d,%d\r\n" % (currentTime, (index + 1), fieldRA[index], fieldDecl[index], starsQueried, starsMatchingCriteria))

    finally:
        # Clean up
        for testIndex in range(len(cameraFilters)):
            summaryFile[testIndex].close()
        brightStarDatabase.disconnect()
            
surveyData = [
#    Filter                      rot  sat    lim
    [BrightStarDatabase.FilterU, 0,    8.82, 15.68],
    #[BrightStarDatabase.FilterU, 0,    7.94, 14.80],
    #[BrightStarDatabase.FilterU, 0,    7.32, 14.17],
    #[BrightStarDatabase.FilterG, 0,   10.62, 17.05],
    #[BrightStarDatabase.FilterG, 0,    9.74, 16.17],
    #[BrightStarDatabase.FilterG, 0,    9.12, 15.54],
    #[BrightStarDatabase.FilterR, 0,   10.44, 16.61],
    #[BrightStarDatabase.FilterR, 0,    9.56, 15.73],
    #[BrightStarDatabase.FilterR, 0,    8.93, 15.10],
    #[BrightStarDatabase.FilterI, 0,   10.10, 16.14],
    #[BrightStarDatabase.FilterI, 0,    9.22, 15.26],
    #[BrightStarDatabase.FilterI, 0,    8.60, 14.63],
    #[BrightStarDatabase.FilterZ, 0,    9.71, 15.56],
    #[BrightStarDatabase.FilterZ, 0,    8.83, 14.68],
    #[BrightStarDatabase.FilterZ, 0,    8.21, 14.06],
    #[BrightStarDatabase.FilterY, 0,    8.90, 14.64],
    #[BrightStarDatabase.FilterY, 0,    8.02, 13.76],
    #[BrightStarDatabase.FilterY, 0,    7.39, 13.13]
    ]
    
# Run survey using data defined above in a single thread environment
def runSingleThread():
    runSurvey(
        cameraFilters = [item[0] for item in surveyData], 
        cameraRotations = [item[1] for item in surveyData],
        lowMagnitudes = [item[2] for item in surveyData], 
        highMagnitudes = [item[3] for item in surveyData], 
        summaryFilePath = "%sSurveySummary-%s.csv" % (outputPath, "%s"))
                 
if __name__ == "__main__":
    runSingleThread()
    
