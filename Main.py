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

outputPath = "D:\\Temp\\"

def runSurvey(cameraFilter, lowMagnitude, highMagnitude, maxDistance, outputFilePath):
    try:
        # Create output file
        outputFile = open(outputFilePath, "w+")
        outputFile.write("Camera Rotation : %f\r\n" % cameraRotation)
        outputFile.write("Camera Filter   : %s\r\n" % cameraFilter)
        outputFile.write("Low Magnitude   : %f\r\n" % lowMagnitude)
        outputFile.write("High Magnitude  : %f\r\n" % highMagnitude)
        outputFile.write("Max Distance    : %f\r\n" % maxDistance)
        outputFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\r\n" % ("CamerRA", "CameraDecl", "Detector", "StarID", "StarRA", "StarDecl", "StarMag", "BrightNeighbors", "OkNeighbors", "DimNeighbors"))
        
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
                # Populate pixel information for stars
                camera.populatePixelFromRADecl(stars, obs)
                # Process star data
                results = processStars(stars, lowMagnitude, highMagnitude, maxDistance)
                # Log results
                for resultIndex in len(results.Index):
                    cameraRA = fieldRA[index]
                    cameraDecl = fieldDecl[index]
                    detector = wavefrontSensor
                    starIndex = results.Index[resultIndex]
                    starID = stars.ID[starIndex]
                    starRA = stars.RA[starIndex]
                    starDecl = stars.Decl[starIndex]
                    starMag = stars.Mag[starIndex]
                    brightNeighbors = results.NumberBelowCriteria[resultIndex]
                    okNeighbors = results.NumberInCriteria[resultIndex]
                    dimNeighbors = results.NumberAboveCriteria[resultIndex]
                    outputFile.write("%f,%f,%s,%d,%f,%f,%f,%d,%d,%d\r\n" % (cameraRA, cameraDecl, detector, starID, starRA, starDecl, starMag, brightNeighbors, okNeighbors, dimNeighbors))
    finally:
        # Clean up
        outputFile.close()
        brightStarDatabase.disconnect()
        
surveyData = { 
#   Filter                         mm   sat    lim      mm   sat    lim      mm   sat    lim
    BrightStarDatabase.FilterU : [[1.0,  8.82, 15.68], [1.5,  7.94, 14.80], [2.0,  7.32, 14.17]],
    BrightStarDatabase.FilterG : [[1.0, 10.62, 17.05], [1.5,  9.74, 16.17], [2.0,  9.12, 15.54]],
    BrightStarDatabase.FilterR : [[1.0, 10.44, 16.61], [1.5,  9.56, 15.73], [2.0,  8.93, 15.10]],
    BrightStarDatabase.FilterI : [[1.0, 10.10, 16.14], [1.5,  9.22, 15.26], [2.0,  8.60, 14.63]],
    BrightStarDatabase.FilterZ : [[1.0,  9.71, 15.56], [1.5,  8.83, 14.68], [2.0,  8.21, 14.06]],
    BrightStarDatabase.FilterY : [[1.0,  8.90, 14.64], [1.5,  8.02, 13.76], [2.0,  7.39, 13.13]]}

# Run survey using data defined above
for filter in surveyData:
    runSurvey(
        cameraFilter = filter, 
        lowMagnitude = surveyData[filter][1], 
        highMagnitude = surveyData[filter][2], 
        maxDistance = surveyData[filter][0],
        outputFilePath = "%sSurveyData-%s-%fmm.csv" % (outputPath, filter, surveyData[filter][0]))