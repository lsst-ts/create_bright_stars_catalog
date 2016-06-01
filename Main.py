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

outputPath = ""

def runSurvey(cameraFilter, lowMagnitude, highMagnitude, maxDistance, summaryFilePath, outputFilePath):
    try:
        # Create summary file
        summaryFile = open(summaryFilePath, "w+")
        summaryFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        summaryFile.write("Camera Filter,%s\r\n" % cameraFilter)
        summaryFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        summaryFile.write("High Magnitude,%f\r\n" % highMagnitude)
        summaryFile.write("Max Distance,%f\r\n" % maxDistance)
    
        # Create output file
        outputFile = open(outputFilePath, "w+")
        outputFile.write("Camera Rotation,%f\r\n" % cameraRotation)
        outputFile.write("Camera Filter,%s\r\n" % cameraFilter)
        outputFile.write("Low Magnitude,%f\r\n" % lowMagnitude)
        outputFile.write("High Magnitude,%f\r\n" % highMagnitude)
        outputFile.write("Max Distance,%f\r\n" % maxDistance)
        outputFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("CamerRA", "CameraDecl", "Detector", "StarID", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors"))
        
        # Setup databases, simulations
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
            summaryFile.write("Field Position (RA, Decl),%f,%f\r\n" % (fieldRA[index], fieldDecl[index]))
            obs = ObservationMetaData(pointingRA=fieldRA[index], pointingDec=fieldDecl[index], rotSkyPos=cameraRotation, mjd=cameraMJD)
            wavefrontSensors = camera.getWavefrontCorners(obs)
            for detector in wavefrontSensors:
                print "Processing detector %s" % detector
                wavefrontSensor = wavefrontSensors[detector]
                # Get stars in this wavefront sensor for this observation field
                summaryFile.write(",\"Detector %s Corners (RA, Decl)\",%f,%f,%f,%f,%f,%f,%f,%f\r\n" % (detector, wavefrontSensor[0][0], wavefrontSensor[0][1], wavefrontSensor[1][0], wavefrontSensor[1][1], wavefrontSensor[2][0], wavefrontSensor[2][1], wavefrontSensor[3][0], wavefrontSensor[3][1]))
                stars = brightStarDatabase.query(cameraFilter, wavefrontSensor[0], wavefrontSensor[1], wavefrontSensor[2], wavefrontSensor[3])
                summaryFile.write(",,Stars Queried,%d\r\n" % len(stars.ID))
                print "Queried %d stars" % len(stars.ID)
                stars.populateDetector(detector)
                camera.removeStarsNotOnDetector(stars, obs)
                summaryFile.write(",,Stars On Detector,%d\r\n" % len(stars.ID))
                # Populate pixel information for stars
                camera.populatePixelFromRADecl(stars, obs)
                # Process star data
                results = survey.processStars(stars, lowMagnitude, highMagnitude, maxDistance)
                summaryFile.write(",,Canidate Stars,%d\r\n" % len(results.Index))
                # Log results
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
                    outputFile.write("%f,%f,\"%s\",%d,%f,%f,%f,%d,%d,%d\r\n" % (cameraRA, cameraDecl, detector, starID, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors))    
    finally:
        # Clean up
        summaryFile.close()
        outputFile.close()
        brightStarDatabase.disconnect()

surveyData = [
#    Filter                      mm   sat    lim
    [BrightStarDatabase.FilterU, 1.0,  8.82, 15.68],
#    [BrightStarDatabase.FilterU, 1.0,  7.94, 14.80],
#    [BrightStarDatabase.FilterU, 1.0,  7.32, 14.17],
    ]
    
# Run survey using data defined above
for item in surveyData:
    runSurvey(
        cameraFilter = item[0], 
        lowMagnitude = item[2], 
        highMagnitude = item[3], 
        maxDistance = item[1],
        summaryFilePath = "%sSurveySummary-%s-%fmm.csv" % (outputPath, item[0], item[1]),
        outputFilePath = "%sSurveyData-%s-%fmm.csv" % (outputPath, item[0], item[1]))