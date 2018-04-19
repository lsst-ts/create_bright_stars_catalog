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

fieldDatabaseFile = "./Fields.txt"
fieldDatabaseAcceptableRADecl = lambda x: x[1] <= 2 or (x[0] >= 0 and x[0] <= 12 and x[1] <= 30)

cameraRotation = 0.0
cameraMJD = 59580.0

# spacingCoefficient = 2.5     # Maximum distance in units of radius one donut must be to another to be considered as a neighbor

# Guider study use
spacingCoefficient = 2.0

checkStarsOnDetector = True # Determine if the stars are on the detector before processing

outputPath = "./surveyData/"

summaryFile = []
detailedLSSTFile = []
detailedLSSTNoATMFile = []
detailedObsFile = []
detailedObsNewFile = []

def runSurvey(cameraFilters, lowMagnitudes, highMagnitudes, maxDistances, summaryFilePath, detailedLSSTFilePath, detailedLSSTNoATMFilePath, detailedObsFilePath, detailedObsNewFilePath):
    try:
        for testIndex in range(len(cameraFilters)):
            cameraFilter = cameraFilters[testIndex]
            lowMagnitude = lowMagnitudes[testIndex]
            highMagnitude = highMagnitudes[testIndex]
            maxDistance = maxDistances[testIndex]
            
            # Create summary file
            # The summary file will contain high level information about each field and each detector
            # It can be used to see total counts of stars but no detail about each star
            summaryFile.append(open(summaryFilePath % (cameraFilter, maxDistance), "w+"))
            summaryFile[testIndex].write("Camera Rotation,%f,,,,,,,,,,,,,,,,,,\r\n" % cameraRotation)
            summaryFile[testIndex].write("Camera Filter,%s,,,,,,,,,,,,,,,,,,\r\n" % cameraFilter)
            summaryFile[testIndex].write("Low Magnitude,%f,,,,,,,,,,,,,,,,,,\r\n" % lowMagnitude)
            summaryFile[testIndex].write("High Magnitude,%f,,,,,,,,,,,,,,,,,,\r\n" % highMagnitude)
            summaryFile[testIndex].write("Max Distance,%f,,,,,,,,,,,,,,,,,,\r\n" % maxDistance)
            summaryFile[testIndex].write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "Corner1RA", "Corner1Decl", "Corner2RA", "Corner2Decl", "Corner3RA", "Corner3Decl", "Corner4RA", "Corner4Decl", "Stars Queried", "Stars on Detector", "LSST Candidate Stars", "LSST No ATM Candidate Stars", "Obs Candidate Stars", "Obs New Candidate Stars", "-99 Stars"))
        
            # Create lsst detail file
            # The detail file will contain low level information about each candidate star in each field on each detector
            detailedLSSTFile.append(open(detailedLSSTFilePath % (cameraFilter, maxDistance), "w+"))
            detailedLSSTFile[testIndex].write("Camera Rotation,%f,,,,,,,,,,\r\n" % cameraRotation)
            detailedLSSTFile[testIndex].write("Camera Filter,%s,,,,,,,,,,\r\n" % cameraFilter)
            detailedLSSTFile[testIndex].write("Low Magnitude,%f,,,,,,,,,,\r\n" % lowMagnitude)
            detailedLSSTFile[testIndex].write("High Magnitude,%f,,,,,,,,,,\r\n" % highMagnitude)
            detailedLSSTFile[testIndex].write("Max Distance,%f,,,,,,,,,,\r\n" % maxDistance)
            detailedLSSTFile[testIndex].write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))
            
            # Create lsst detail no atm file
            # The detail file will contain low level information about each candidate star in each field on each detector
            detailedLSSTNoATMFile.append(open(detailedLSSTNoATMFilePath % (cameraFilter, maxDistance), "w+"))
            detailedLSSTNoATMFile[testIndex].write("Camera Rotation,%f,,,,,,,,,,\r\n" % cameraRotation)
            detailedLSSTNoATMFile[testIndex].write("Camera Filter,%s,,,,,,,,,,\r\n" % cameraFilter)
            detailedLSSTNoATMFile[testIndex].write("Low Magnitude,%f,,,,,,,,,,\r\n" % lowMagnitude)
            detailedLSSTNoATMFile[testIndex].write("High Magnitude,%f,,,,,,,,,,\r\n" % highMagnitude)
            detailedLSSTNoATMFile[testIndex].write("Max Distance,%f,,,,,,,,,,\r\n" % maxDistance)
            detailedLSSTNoATMFile[testIndex].write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))
            
            # Create obs detail file
            # The detail file will contain low level information about each candidate star in each field on each detector
            detailedObsFile.append(open(detailedObsFilePath % (cameraFilter, maxDistance), "w+"))
            detailedObsFile[testIndex].write("Camera Rotation,%f,,,,,,,,,,\r\n" % cameraRotation)
            detailedObsFile[testIndex].write("Camera Filter,%s,,,,,,,,,,\r\n" % cameraFilter)
            detailedObsFile[testIndex].write("Low Magnitude,%f,,,,,,,,,,\r\n" % lowMagnitude)
            detailedObsFile[testIndex].write("High Magnitude,%f,,,,,,,,,,\r\n" % highMagnitude)
            detailedObsFile[testIndex].write("Max Distance,%f,,,,,,,,,,\r\n" % maxDistance)
            detailedObsFile[testIndex].write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))
            
            # Create obs detail new file
            # The detail file will contain low level information about each candidate star in each field on each detector
            detailedObsNewFile.append(open(detailedObsNewFilePath % (cameraFilter, maxDistance), "w+"))
            detailedObsNewFile[testIndex].write("Camera Rotation,%f,,,,,,,,,,\r\n" % cameraRotation)
            detailedObsNewFile[testIndex].write("Camera Filter,%s,,,,,,,,,,\r\n" % cameraFilter)
            detailedObsNewFile[testIndex].write("Low Magnitude,%f,,,,,,,,,,\r\n" % lowMagnitude)
            detailedObsNewFile[testIndex].write("High Magnitude,%f,,,,,,,,,,\r\n" % highMagnitude)
            detailedObsNewFile[testIndex].write("Max Distance,%f,,,,,,,,,,\r\n" % maxDistance)
            detailedObsNewFile[testIndex].write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("Timestamp", "FieldIndex", "CameraRA", "CameraDecl", "Detector", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors", "IgnoredNeighbors"))

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
            print("Field #%d of %d" % ((index + 1), len(fieldRA)))
            
            # Get corners of wavefront sensors for this observation field
            obs = ObservationMetaData(pointingRA=fieldRA[index], pointingDec=fieldDecl[index], rotSkyPos=cameraRotation, mjd=cameraMJD)
            wavefrontSensors = camera.getWavefrontCorners(obs)
            for detector in wavefrontSensors:
                print("\tProcessing detector %s" % detector)
                wavefrontSensor = wavefrontSensors[detector]
                
                # Get stars in this wavefront sensor for this observation field
                stars = brightStarDatabase.query(wavefrontSensor[0], wavefrontSensor[1], wavefrontSensor[2], wavefrontSensor[3])
                starsQueried = len(stars.RA)
                print("\t\tStars queried %d" % starsQueried)
                
                # Populate detector information for the stars
                stars.populateDetector(detector)
                
                # Populate pixel information for stars
                camera.populatePixelFromRADecl(stars, obs)
                
                if (checkStarsOnDetector):
                    # Remove stars that are not on the detector
                    camera.removeStarsNotOnDetectorSimple(stars, obs)

                starsOnDetector = len(stars.RA)
                print("\t\tStars on detector %d" % starsOnDetector)
                
                # Process star data
                for testIndex in range(len(cameraFilters)):
                    cameraFilter = cameraFilters[testIndex]
                    lowMagnitude = lowMagnitudes[testIndex]
                    highMagnitude = highMagnitudes[testIndex]
                    maxDistance = maxDistances[testIndex]
                    
                    print("\t\tFilter %s Distance %.3f" % (cameraFilter, maxDistance))
                    
                    results, obsMagLambda, obsMagNewLambda, lsstMagLambda, lsstMagNoATMLambda = survey.processStars(stars, cameraFilter, lowMagnitude, highMagnitude, maxDistance)
                    lsstCandidateStars = len(results.LSSTIndex)
                    print("\t\t\tLSST Candidate stars %d" % lsstCandidateStars)
                    lsstNoATMCandidateStars = len(results.LSSTNoATMIndex)
                    print("\t\t\tLSST No ATM Candidate stars %d" % lsstNoATMCandidateStars)
                    obsCandidateStars = len(results.ObsIndex)
                    print("\t\t\tObs Candidate stars %d" % obsCandidateStars)
                    obsNewCandidateStars = len(results.ObsNewIndex)
                    print("\t\t\tObs New Candidate stars %d" % obsNewCandidateStars)
                    
                    # Determine number of -99 stars
                    neg99Count = 0
                    for starIndex in range(len(stars.RA)):
                        if obsMagLambda(stars, starIndex) == -99:
                            neg99Count += 1
                    print("\t\t\t-99 Stars %d" % neg99Count)
                    
                    # Log summary results
                    currentTime = time.time()
                    summaryFile[testIndex].write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), fieldRA[index], fieldDecl[index], detector, wavefrontSensor[0][0], wavefrontSensor[0][1], wavefrontSensor[1][0], wavefrontSensor[1][1], wavefrontSensor[2][0], wavefrontSensor[2][1], wavefrontSensor[3][0], wavefrontSensor[3][1], starsQueried, starsOnDetector, lsstCandidateStars, lsstNoATMCandidateStars, obsCandidateStars, obsNewCandidateStars, neg99Count))
                    
                    # Log lsst detailed results
                    for resultIndex in range(len(results.LSSTIndex)):
                        cameraRA = fieldRA[index]
                        cameraDecl = fieldDecl[index]
                        detector = detector
                        starIndex = results.LSSTIndex[resultIndex]
                        starRA = stars.RA[starIndex]
                        starDecl = stars.Decl[starIndex]
                        starMag = lsstMagLambda(stars, starIndex)
                        brightNeighbors = results.LSSTNumberBelowCriteria[resultIndex]
                        okNeighbors = results.LSSTNumberInCriteria[resultIndex]
                        dimNeighbors = results.LSSTNumberAboveCriteria[resultIndex]
                        ignoredNeighbors = results.LSSTNumberIgnored[resultIndex]
                        detailedLSSTFile[testIndex].write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))
                        
                    # Log lsst no atm detailed results
                    for resultIndex in range(len(results.LSSTNoATMIndex)):
                        cameraRA = fieldRA[index]
                        cameraDecl = fieldDecl[index]
                        detector = detector
                        starIndex = results.LSSTNoATMIndex[resultIndex]
                        starRA = stars.RA[starIndex]
                        starDecl = stars.Decl[starIndex]
                        starMag = lsstMagNoATMLambda(stars, starIndex)
                        brightNeighbors = results.LSSTNoATMNumberBelowCriteria[resultIndex]
                        okNeighbors = results.LSSTNoATMNumberInCriteria[resultIndex]
                        dimNeighbors = results.LSSTNoATMNumberAboveCriteria[resultIndex]
                        ignoredNeighbors = results.LSSTNoATMNumberIgnored[resultIndex]
                        detailedLSSTNoATMFile[testIndex].write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))    
                        
                    # Log obs detailed results
                    for resultIndex in range(len(results.ObsIndex)):
                        cameraRA = fieldRA[index]
                        cameraDecl = fieldDecl[index]
                        detector = detector
                        starIndex = results.ObsIndex[resultIndex]
                        starRA = stars.RA[starIndex]
                        starDecl = stars.Decl[starIndex]
                        starMag = obsMagLambda(stars, starIndex)
                        brightNeighbors = results.ObsNumberBelowCriteria[resultIndex]
                        okNeighbors = results.ObsNumberInCriteria[resultIndex]
                        dimNeighbors = results.ObsNumberAboveCriteria[resultIndex]
                        ignoredNeighbors = results.ObsNumberIgnored[resultIndex]
                        detailedObsFile[testIndex].write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))    
                        
                    # Log obs detailed results
                    for resultIndex in range(len(results.ObsNewIndex)):
                        cameraRA = fieldRA[index]
                        cameraDecl = fieldDecl[index]
                        detector = detector
                        starIndex = results.ObsNewIndex[resultIndex]
                        starRA = stars.RA[starIndex]
                        starDecl = stars.Decl[starIndex]
                        starMag = obsMagNewLambda(stars, starIndex)
                        brightNeighbors = results.ObsNewNumberBelowCriteria[resultIndex]
                        okNeighbors = results.ObsNewNumberInCriteria[resultIndex]
                        dimNeighbors = results.ObsNewNumberAboveCriteria[resultIndex]
                        ignoredNeighbors = results.ObsNewNumberIgnored[resultIndex]
                        detailedObsNewFile[testIndex].write("%f,%d,%f,%f,\"%s\",%f,%f,%f,%d,%d,%d,%d\r\n" % (currentTime, (index + 1), cameraRA, cameraDecl, detector, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors, ignoredNeighbors))    

    finally:
        # Clean up
        for testIndex in range(len(cameraFilters)):
            summaryFile[testIndex].close()
            detailedLSSTFile[testIndex].close()
            detailedLSSTNoATMFile[testIndex].close()
            detailedObsFile[testIndex].close()
            detailedObsNewFile[testIndex].close()
        brightStarDatabase.disconnect()

def star_runSurvey(args):
    return runSurvey(*args)
            
# surveyData = [
# #    Filter                      pix -> mm                                         sat    lim
#     [BrightStarDatabase.FilterU, 42 * StarData.PixelSizeInMM * spacingCoefficient,  8.82, 15.68],
#     [BrightStarDatabase.FilterU, 63 * StarData.PixelSizeInMM * spacingCoefficient,  7.94, 14.80],
#     [BrightStarDatabase.FilterU, 84 * StarData.PixelSizeInMM * spacingCoefficient,  7.32, 14.17],
#     [BrightStarDatabase.FilterG, 42 * StarData.PixelSizeInMM * spacingCoefficient, 10.62, 17.05],
#     [BrightStarDatabase.FilterG, 63 * StarData.PixelSizeInMM * spacingCoefficient,  9.74, 16.17],
#     [BrightStarDatabase.FilterG, 84 * StarData.PixelSizeInMM * spacingCoefficient,  9.12, 15.54],
#     [BrightStarDatabase.FilterR, 42 * StarData.PixelSizeInMM * spacingCoefficient, 10.44, 16.61],
#     [BrightStarDatabase.FilterR, 63 * StarData.PixelSizeInMM * spacingCoefficient,  9.56, 15.73],
#     [BrightStarDatabase.FilterR, 84 * StarData.PixelSizeInMM * spacingCoefficient,  8.93, 15.10],
#     [BrightStarDatabase.FilterI, 42 * StarData.PixelSizeInMM * spacingCoefficient, 10.10, 16.14],
#     [BrightStarDatabase.FilterI, 63 * StarData.PixelSizeInMM * spacingCoefficient,  9.22, 15.26],
#     [BrightStarDatabase.FilterI, 84 * StarData.PixelSizeInMM * spacingCoefficient,  8.60, 14.63],
#     [BrightStarDatabase.FilterZ, 42 * StarData.PixelSizeInMM * spacingCoefficient,  9.71, 15.56],
#     [BrightStarDatabase.FilterZ, 63 * StarData.PixelSizeInMM * spacingCoefficient,  8.83, 14.68],
#     [BrightStarDatabase.FilterZ, 84 * StarData.PixelSizeInMM * spacingCoefficient,  8.21, 14.06],
#     [BrightStarDatabase.FilterY, 42 * StarData.PixelSizeInMM * spacingCoefficient,  8.90, 14.64],
#     [BrightStarDatabase.FilterY, 63 * StarData.PixelSizeInMM * spacingCoefficient,  8.02, 13.76],
#     [BrightStarDatabase.FilterY, 84 * StarData.PixelSizeInMM * spacingCoefficient,  7.39, 13.13]
#     ]

surveyData = [
#    Filter                      pix -> mm                                         sat    lim
    [BrightStarDatabase.FilterU, 3.5 * StarData.PixelSizeInMM * spacingCoefficient,  9.37, 13.0],
    [BrightStarDatabase.FilterG, 3.5 * StarData.PixelSizeInMM * spacingCoefficient, 10.37, 13.0],
    [BrightStarDatabase.FilterR, 3.5 * StarData.PixelSizeInMM * spacingCoefficient, 10.47, 13.0],
    [BrightStarDatabase.FilterI, 3.5 * StarData.PixelSizeInMM * spacingCoefficient, 10.47, 13.0],
    [BrightStarDatabase.FilterZ, 3.5 * StarData.PixelSizeInMM * spacingCoefficient,  9.97, 13.0],
    [BrightStarDatabase.FilterY, 3.5 * StarData.PixelSizeInMM * spacingCoefficient,  8.57, 13.0],
    ]
    
# Run survey using data defined above in a single thread environment
def runSingleThread():
    runSurvey(
        cameraFilters = [item[0] for item in surveyData], 
        lowMagnitudes = [item[2] for item in surveyData], 
        highMagnitudes = [item[3] for item in surveyData], 
        maxDistances = [item[1] for item in surveyData],
        summaryFilePath = "%sSurveySummary-%s-%smm.csv" % (outputPath, "%s", "%f"),
        detailedLSSTFilePath = "%sSurveyLSST-%s-%smm.csv" % (outputPath, "%s", "%f"),
        detailedLSSTNoATMFilePath = "%sSurveyLSSTNoATM-%s-%smm.csv" % (outputPath, "%s", "%f"),
        detailedObsFilePath = "%sSurveyObs-%s-%smm.csv" % (outputPath, "%s", "%f"),
        detailedObsNewFilePath = "%sSurveyObsNew-%s-%smm.csv" % (outputPath, "%s", "%f"))
          
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
    