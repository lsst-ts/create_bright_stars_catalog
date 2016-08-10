import BrightStarDatabase
import FieldDatabase
import CameraData
import SkyCoverageSurvey
import StarData
import time
import itertools

from lsst.sims.utils import ObservationMetaData
from multiprocessing import Pool, freeze_support

brightStarDatabaseHost = "localhost:51433"
brightStarDatabaseUser = "LSST-2"
brightStarDatabasePassword = "L$$TUser"
brightStarDatabaseDatabase = "LSSTCATSIM"

fieldDatabaseFile = ".\Fields.txt"
fieldDatabaseAcceptableRADecl = lambda x: x[1] <= 2 or (x[0] >= 0 and x[0] <= 12 and x[1] <= 30)

cameraRotation = 0.0
cameraMJD = 59580.0

spacingCoefficient = 2.5     # Maximum distance in units of radius one donut must be to another to be considered as a neighbor
checkStarsOnDetector = True # Determine if the stars are on the detector before processing

outputPath = ""

def runSurvey(cameraFilter, lowMagnitude, highMagnitude, maxDistance, summaryFilePath, detailedLSSTFilePath, detailedLSSTNoATMFilePath, detailedObsFilePath, detailedObsNewFilePath):
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
        summaryFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "Corner1RA", "Corner1Decl", "Corner2RA", "Corner2Decl", "Corner3RA", "Corner3Decl", "Corner4RA", "Corner4Decl", "Stars Queried", "Stars on Detector", "LSST Candidate Stars", "LSST No ATM Candidate Stars", "Obs Candidate Stars", "Obs New Candidate Stars", "-99 Stars"))
    
        # Create lsst detail file
        # The detail file will contain low level information about each candidate star in each field on each detector
        detailedLSSTFile = open(detailedLSSTFilePath, "w+")
        detailedLSSTFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        detailedLSSTFile.write("Camera Filter,%s\r\n" % cameraFilter)
        detailedLSSTFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        detailedLSSTFile.write("High Magnitude,%f\r\n" % highMagnitude)
        detailedLSSTFile.write("Max Distance,%f\r\n" % maxDistance)
        detailedLSSTFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))
        
        # Create lsst detail no atm file
        # The detail file will contain low level information about each candidate star in each field on each detector
        detailedLSSTNoATMFile = open(detailedLSSTNoATMFilePath, "w+")
        detailedLSSTNoATMFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        detailedLSSTNoATMFile.write("Camera Filter,%s\r\n" % cameraFilter)
        detailedLSSTNoATMFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        detailedLSSTNoATMFile.write("High Magnitude,%f\r\n" % highMagnitude)
        detailedLSSTNoATMFile.write("Max Distance,%f\r\n" % maxDistance)
        detailedLSSTNoATMFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))
        
        # Create obs detail file
        # The detail file will contain low level information about each candidate star in each field on each detector
        detailedObsFile = open(detailedObsFilePath, "w+")
        detailedObsFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        detailedObsFile.write("Camera Filter,%s\r\n" % cameraFilter)
        detailedObsFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        detailedObsFile.write("High Magnitude,%f\r\n" % highMagnitude)
        detailedObsFile.write("Max Distance,%f\r\n" % maxDistance)
        detailedObsFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))
        
        # Create obs detail new file
        # The detail file will contain low level information about each candidate star in each field on each detector
        detailedObsNewFile = open(detailedObsNewFilePath, "w+")
        detailedObsNewFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        detailedObsNewFile.write("Camera Filter,%s\r\n" % cameraFilter)
        detailedObsNewFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        detailedObsNewFile.write("High Magnitude,%f\r\n" % highMagnitude)
        detailedObsNewFile.write("Max Distance,%f\r\n" % maxDistance)
        detailedObsNewFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))

        # Setup databases, simulations, and survey
        brightStarDatabase = BrightStarDatabase.BrightStarDatabase()
        fieldDatabase = FieldDatabase.FieldDatabase("Fields.txt", fieldDatabaseAcceptableRADecl)
        camera = CameraData.CameraData()
        survey = SkyCoverageSurvey.SkyCoverageSurvey()
        
        # Connect to database
        brightStarDatabase.connect(brightStarDatabaseHost, brightStarDatabaseUser, brightStarDatabasePassword, brightStarDatabaseDatabase)
     
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
                starsQueried = len(stars.RA)
                print "\t\tStars queried %d" % starsQueried
                
                # Populate detector information for the stars
                stars.populateDetector(detector)
                
                # Populate pixel information for stars
                camera.populatePixelFromRADecl(stars, obs)
                
                if (checkStarsOnDetector):
                    # Remove stars that are not on the detector
                    camera.removeStarsNotOnDetectorSimple(stars, obs)

                starsOnDetector = len(stars.RA)
                print "\t\tStars on detector %d" % starsOnDetector

                # Process star data
                results = survey.processStars(stars, lowMagnitude, highMagnitude, maxDistance)
                lsstCandidateStars = len(results.LSSTIndex)
                print "\t\tLSST Candidate stars %d" % lsstCandidateStars
                lsstNoATMCandidateStars = len(results.LSSTNoATMIndex)
                print "\t\tLSST No ATM Candidate stars %d" % lsstNoATMCandidateStars
                obsCandidateStars = len(results.ObsIndex)
                print "\t\tObs Candidate stars %d" % obsCandidateStars
                obsNewCandidateStars = len(results.ObsNewIndex)
                print "\t\tObs New Candidate stars %d" % obsNewCandidateStars
                
                # Determine number of -99 stars
                neg99Count = 0
                for starIndex in range(len(stars.RA)):
                    if stars.ObsMag[starIndex] == -99:
                        neg99Count += 1
                print "\t\t-99 Stars %d" % neg99Count
                
                # Log summary results
                currentTime = time.time()
                summaryFile.write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), fieldRA[index], fieldDecl[index], detector, wavefrontSensor[0][0], wavefrontSensor[0][1], wavefrontSensor[1][0], wavefrontSensor[1][1], wavefrontSensor[2][0], wavefrontSensor[2][1], wavefrontSensor[3][0], wavefrontSensor[3][1], starsQueried, starsOnDetector, lsstCandidateStars, lsstNoATMCandidateStars, obsCandidateStars, obsNewCandidateStars, neg99Count))
                
                # Log lsst detailed results
                for resultIndex in range(len(results.LSSTIndex)):
                    cameraRA = fieldRA[index]
                    cameraDecl = fieldDecl[index]
                    detector = detector
                    starIndex = results.LSSTIndex[resultIndex]
                    starRA = stars.RA[starIndex]
                    starDecl = stars.Decl[starIndex]
                    starMag = stars.LSSTMag[starIndex]
                    brightNeighbors = results.LSSTNumberBelowCriteria[resultIndex]
                    okNeighbors = results.LSSTNumberInCriteria[resultIndex]
                    dimNeighbors = results.LSSTNumberAboveCriteria[resultIndex]
                    ignoredNeighbors = results.LSSTNumberIgnored[resultIndex]
                    detailedLSSTFile.write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))
                    
                # Log lsst no atm detailed results
                for resultIndex in range(len(results.LSSTNoATMIndex)):
                    cameraRA = fieldRA[index]
                    cameraDecl = fieldDecl[index]
                    detector = detector
                    starIndex = results.LSSTNoATMIndex[resultIndex]
                    starRA = stars.RA[starIndex]
                    starDecl = stars.Decl[starIndex]
                    starMag = stars.LSSTMagNoATM[starIndex]
                    brightNeighbors = results.LSSTNoATMNumberBelowCriteria[resultIndex]
                    okNeighbors = results.LSSTNoATMNumberInCriteria[resultIndex]
                    dimNeighbors = results.LSSTNoATMNumberAboveCriteria[resultIndex]
                    ignoredNeighbors = results.LSSTNoATMNumberIgnored[resultIndex]
                    detailedLSSTNoATMFile.write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))    
                    
                # Log obs detailed results
                for resultIndex in range(len(results.ObsIndex)):
                    cameraRA = fieldRA[index]
                    cameraDecl = fieldDecl[index]
                    detector = detector
                    starIndex = results.ObsIndex[resultIndex]
                    starRA = stars.RA[starIndex]
                    starDecl = stars.Decl[starIndex]
                    starMag = stars.ObsMag[starIndex]
                    brightNeighbors = results.ObsNumberBelowCriteria[resultIndex]
                    okNeighbors = results.ObsNumberInCriteria[resultIndex]
                    dimNeighbors = results.ObsNumberAboveCriteria[resultIndex]
                    ignoredNeighbors = results.ObsNumberIgnored[resultIndex]
                    detailedObsFile.write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))    
                    
                # Log obs detailed results
                for resultIndex in range(len(results.ObsNewIndex)):
                    cameraRA = fieldRA[index]
                    cameraDecl = fieldDecl[index]
                    detector = detector
                    starIndex = results.ObsNewIndex[resultIndex]
                    starRA = stars.RA[starIndex]
                    starDecl = stars.Decl[starIndex]
                    starMag = stars.ObsMag[starIndex]
                    brightNeighbors = results.ObsNewNumberBelowCriteria[resultIndex]
                    okNeighbors = results.ObsNewNumberInCriteria[resultIndex]
                    dimNeighbors = results.ObsNewNumberAboveCriteria[resultIndex]
                    ignoredNeighbors = results.ObsNewNumberIgnored[resultIndex]
                    detailedObsNewFile.write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))    

    finally:
        # Clean up
        summaryFile.close()
        detailedLSSTFile.close()
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
            detailedLSSTFilePath = "%sSurveyLSST-%s-%fmm.csv" % (outputPath, item[0], item[1]),
            detailedLSSTNoATMFilePath = "%sSurveyLSSTNoATM-%s-%fmm.csv" % (outputPath, item[0], item[1]),
            detailedObsFilePath = "%sSurveyObs-%s-%fmm.csv" % (outputPath, item[0], item[1]),
            detailedObsNewFilePath = "%sSurveyObsNew-%s-%fmm.csv" % (outputPath, item[0], item[1]))
            
          
# Run survey using data defined above in a multi threaded environment
def runMultiThread():
    pool = Pool()
    args = []
    for item in surveyData:
        args.append((item[0], item[2], item[3], item[1], "%sSurveySummary-%s-%fmm.csv" % (outputPath, item[0], item[1]), "%sSurveyLSST-%s-%fmm.csv" % (outputPath, item[0], item[1]), "%sSurveyObs-%s-%fmm.csv" % (outputPath, item[0], item[1])))
    pool.map(star_runSurvey, args)
       
if __name__ == "__main__":
    freeze_support()
    runSingleThread()
    