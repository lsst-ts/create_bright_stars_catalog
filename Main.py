import BrightStarDatabase
import FieldDatabase
import CameraData
import SkyCoverageSurvey
import StarData
import time
import itertools

from lsst.sims.utils import ObservationMetaData
from multiprocessing import Pool, freeze_support

brightStarDatabaseHost = "140.252.32.27"
brightStarDatabasePort = 3306
brightStarDatabaseUser = "lsstwasadmin"
brightStarDatabasePassword = "lsstwasadmin"
brightStarDatabaseDatabase = "BrightStarCatalog"

fieldDatabaseFile = ".\Fields.txt"
fieldDatabaseAcceptableRADecl = lambda x: x[1] <= 2 or (x[0] >= 0 and x[0] <= 12 and x[1] <= 30)

cameraRotation = 32.0
cameraMJD = 59580.0

spacingCoefficient = 2.0 # Maximum distance in units of radius one donut must be to another to be considered as a neighbor

outputPath = ""

def runSurvey(cameraFilter, lowMagnitude, highMagnitude, maxDistance, summaryFilePath, detailedFilePath):
    try:
        # Create summary file
        # The summary file will contain high level information about each field and each detector
        # It can be used to see total counts of stars but no detail about each star
        summaryFile = open(summaryFilePath, "w+")
        summaryFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        summaryFile.write("Camera Filter,%s\r\n" % cameraFilter)
        summaryFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        summaryFile.write("High Magnitude,%f\r\n" % highMagnitude)
        summaryFile.write("Max Distance,%f\r\n" % maxDistance)
        summaryFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CamerRA", "CameraDecl", "Detector", "Corner1RA", "Corner1Decl", "Corner2RA", "Corner2Decl", "Corner3RA", "Corner3Decl", "Corner4RA", "Corner4Decl", "Stars Queried", "Stars on Detector", "Candidate Stars"))
    
        # Create detail file
        # The detail file will contain low level information about each candidate star in each field on each detector
        detailedFile = open(detailedFilePath, "w+")
        detailedFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        detailedFile.write("Camera Filter,%s\r\n" % cameraFilter)
        detailedFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        detailedFile.write("High Magnitude,%f\r\n" % highMagnitude)
        detailedFile.write("Max Distance,%f\r\n" % maxDistance)
        detailedFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CamerRA", "CameraDecl", "Detector", "StarID", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors"))
        
        # Setup databases, simulations, and survey
        brightStarDatabase = BrightStarDatabase.BrightStarDatabase()
        fieldDatabase = FieldDatabase.FieldDatabase("Fields.txt", fieldDatabaseAcceptableRADecl)
        camera = CameraData.CameraData()
        survey = SkyCoverageSurvey.SkyCoverageSurvey()
        
        # Connect to database
        brightStarDatabase.connect(brightStarDatabaseHost, brightStarDatabasePort, brightStarDatabaseUser, brightStarDatabasePassword, brightStarDatabaseDatabase)
     
        # Get observation fields
        fieldRA, fieldDecl = fieldDatabase.getRADecl()
        for index in range(len(fieldRA)):
            print "Field #%d of %d" % ((index + 1), len(fieldRA))
            
            # Get corners of wavefront sensors for this observation field
            obs = ObservationMetaData(pointingRA=fieldRA[index], pointingDec=fieldDecl[index], rotSkyPos=cameraRotation, mjd=cameraMJD)
            wavefrontSensors = camera.getWavefrontCorners(obs)
            for detector in wavefrontSensors:
                print "\tProcessing detector %s" % detector
                wavefrontSensor = wavefrontSensors[detector]
                
                # Get stars in this wavefront sensor for this observation field
                stars = brightStarDatabase.query(cameraFilter, wavefrontSensor[0], wavefrontSensor[1], wavefrontSensor[2], wavefrontSensor[3])
                starsQueried = len(stars.ID)
                print "\t\tStars queried %d" % starsQueried
                
                # Populate detector information for the stars
                stars.populateDetector(detector)
                
                # Remove stars that are not on the detector
                camera.removeStarsNotOnDetector(stars, obs)
                starsOnDetector = len(stars.ID)
                print "\t\tStars on detector %d" % starsOnDetector
                
                # Populate pixel information for stars
                camera.populatePixelFromRADecl(stars, obs)
                
                # Process star data
                results = survey.processStars(stars, lowMagnitude, highMagnitude, maxDistance)
                candidateStars = len(results.Index)
                print "\t\tCandidate stars %d" % candidateStars
                
                # Log summary results
                currentTime = time.time()
                summaryFile.write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d\r\n" % (currentTime, (index + 1), fieldRA[index], fieldDecl[index], detector, wavefrontSensor[0][0], wavefrontSensor[0][1], wavefrontSensor[1][0], wavefrontSensor[1][1], wavefrontSensor[2][0], wavefrontSensor[2][1], wavefrontSensor[3][0], wavefrontSensor[3][1], starsQueried, starsOnDetector, candidateStars))
                
                # Log detailed results
                for resultIndex in range(len(results.Index)):
                    cameraRA = fieldRA[index]
                    cameraDecl = fieldDecl[index]
                    detector = detector
                    starIndex = results.Index[resultIndex]
                    starID = stars.ID[starIndex]
                    starRA = stars.RA[starIndex]
                    starDecl = stars.Decl[starIndex]
                    starMag = stars.Mag[starIndex]
                    brightNeighbors = results.NumberBelowCriteria[resultIndex]
                    okNeighbors = results.NumberInCriteria[resultIndex]
                    dimNeighbors = results.NumberAboveCriteria[resultIndex]
                    detailedFile.write("%f,%d,%f,%f,\"%s\",%d,%f,%f,%f,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starID, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors))    
    finally:
        # Clean up
        summaryFile.close()
        detailedFile.close()
        brightStarDatabase.disconnect()

def star_runSurvey(args):
    return runSurvey(*args)
            
surveyData = [
#    Filter                      pix -> mm                                         sat    lim
    [BrightStarDatabase.FilterU, 42 * StarData.PixelSizeInMM * spacingCoefficient,  8.82, 15.68],
    [BrightStarDatabase.FilterU, 63 * StarData.PixelSizeInMM * spacingCoefficient,  7.94, 14.80],
    [BrightStarDatabase.FilterU, 84 * StarData.PixelSizeInMM * spacingCoefficient,  7.32, 14.17],
    [BrightStarDatabase.FilterG, 42 * StarData.PixelSizeInMM * spacingCoefficient, 10.62, 17.05],
    [BrightStarDatabase.FilterG, 63 * StarData.PixelSizeInMM * spacingCoefficient,  9.74, 16.17],
    [BrightStarDatabase.FilterG, 84 * StarData.PixelSizeInMM * spacingCoefficient,  9.12, 15.54],
    [BrightStarDatabase.FilterR, 42 * StarData.PixelSizeInMM * spacingCoefficient, 10.44, 16.61],
    [BrightStarDatabase.FilterR, 63 * StarData.PixelSizeInMM * spacingCoefficient,  9.56, 15.73],
    [BrightStarDatabase.FilterR, 84 * StarData.PixelSizeInMM * spacingCoefficient,  8.93, 15.10],
    [BrightStarDatabase.FilterI, 42 * StarData.PixelSizeInMM * spacingCoefficient, 10.10, 16.14],
    [BrightStarDatabase.FilterI, 63 * StarData.PixelSizeInMM * spacingCoefficient,  9.22, 15.26],
    [BrightStarDatabase.FilterI, 84 * StarData.PixelSizeInMM * spacingCoefficient,  8.60, 14.63],
    [BrightStarDatabase.FilterZ, 42 * StarData.PixelSizeInMM * spacingCoefficient,  9.71, 15.56],
    [BrightStarDatabase.FilterZ, 63 * StarData.PixelSizeInMM * spacingCoefficient,  8.83, 14.68],
    [BrightStarDatabase.FilterZ, 84 * StarData.PixelSizeInMM * spacingCoefficient,  8.21, 14.06],
    [BrightStarDatabase.FilterY, 42 * StarData.PixelSizeInMM * spacingCoefficient,  8.90, 14.64],
    [BrightStarDatabase.FilterY, 63 * StarData.PixelSizeInMM * spacingCoefficient,  8.02, 13.76],
    [BrightStarDatabase.FilterY, 84 * StarData.PixelSizeInMM * spacingCoefficient,  7.39, 13.13]
    ]
    
# Run survey using data defined above in a single thread environment
def runSingleThread():
    for item in surveyData:
        runSurvey(
            cameraFilter = item[0], 
            lowMagnitude = item[2], 
            highMagnitude = item[3], 
            maxDistance = item[1],
            summaryFilePath = "%sSurveySummary-%s-%fmm.csv" % (outputPath, item[0], item[1]),
            detailedFilePath = "%sSurveyDetail-%s-%fmm.csv" % (outputPath, item[0], item[1]))
          
# Run survey using data defined above in a multi threaded environment
def runMultiThread():
    pool = Pool()
    args = []
    for item in surveyData:
        args.append((item[0], item[2], item[3], item[1], "%sSurveySummary-%s-%fmm.csv" % (outputPath, item[0], item[1]), "%sSurveyDetail-%s-%fmm.csv" % (outputPath, item[0], item[1])))
    pool.map(star_runSurvey, args)
       
if __name__ == "__main__":
    freeze_support()
    runMultiThread()
    