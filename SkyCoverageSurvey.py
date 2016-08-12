import numpy
import scipy
import scipy.spatial
import StarData
import unittest
import BrightStarDatabase

MinRAPixel = 0
MaxRAPixel = 4095
MinDeclPixel = 0
MaxDeclPixel = 2047

class SkyCoverageResult(object):
    def __init__(self):
        self.LSSTIndex = []
        self.LSSTNumberBelowCriteria = []
        self.LSSTNumberInCriteria = []
        self.LSSTNumberAboveCriteria = []
        self.LSSTNumberIgnored = []
        self.LSSTNoATMIndex = []
        self.LSSTNoATMNumberBelowCriteria = []
        self.LSSTNoATMNumberInCriteria = []
        self.LSSTNoATMNumberAboveCriteria = []
        self.LSSTNoATMNumberIgnored = []
        self.ObsIndex = []
        self.ObsNumberBelowCriteria = []
        self.ObsNumberInCriteria = []
        self.ObsNumberAboveCriteria = []
        self.ObsNumberIgnored = []
        self.ObsNewIndex = []
        self.ObsNewNumberBelowCriteria = []
        self.ObsNewNumberInCriteria = []
        self.ObsNewNumberAboveCriteria = []
        self.ObsNewNumberIgnored = []
    
class SkyCoverageSurvey(object):
    def processStars(self, stars, filter, lowMagnitude, highMagnitude, maxDistance):
        """
        Takes a list of stars and determines which stars are candidates for wave front sensing by looking at their
        distance from the edge of the detector, and their magnitude.
        
        @param stars [in] The input set of stars that are on the detector and have had their *InMM fields populated.
        
        @param filter [in] The filter (using BrightStarDatabase.Filter[U, G, R, I, Z, Y]) to perform calculations on.
        
        @param lowMagnitude [in] The minimum magnitude (magnitude that causes detector saturation).
        
        @param highMagnitude [in] The maximum magnitude (magnitude that is too dim to get good signal to noise).
        
        @param maxDistance [in] The maximum distance in mm to check around a candidate star.
        """
        
        obsMagLambda = lambda stars, index: stars.ObsMagU[index]
        obsMagNewLambda = lambda stars, index: stars.ObsMagUNew[index]
        lsstMagLambda = lambda stars, index: stars.LSSTMagU[index]
        lsstMagNoATMLambda = lambda stars, index: stars.LSSTMagUNoATM[index]
        if filter is BrightStarDatabase.FilterG:
            obsMagLambda = lambda stars, index: stars.ObsMagG[index]
            obsMagNewLambda = lambda stars, index: stars.ObsMagGNew[index]
            lsstMagLambda = lambda stars, index: stars.LSSTMagG[index]
            lsstMagNoATMLambda = lambda stars, index: stars.LSSTMagGNoATM[index]
        elif filter is BrightStarDatabase.FilterR:
            obsMagLambda = lambda stars, index: stars.ObsMagR[index]
            obsMagNewLambda = lambda stars, index: stars.ObsMagRNew[index]
            lsstMagLambda = lambda stars, index: stars.LSSTMagR[index]
            lsstMagNoATMLambda = lambda stars, index: stars.LSSTMagRNoATM[index]
        elif filter is BrightStarDatabase.FilterI:
            obsMagLambda = lambda stars, index: stars.ObsMagI[index]
            obsMagNewLambda = lambda stars, index: stars.ObsMagINew[index]
            lsstMagLambda = lambda stars, index: stars.LSSTMagI[index]
            lsstMagNoATMLambda = lambda stars, index: stars.LSSTMagINoATM[index]
        elif filter is BrightStarDatabase.FilterZ:
            obsMagLambda = lambda stars, index: stars.ObsMagZ[index]
            obsMagNewLambda = lambda stars, index: stars.ObsMagZNew[index]
            lsstMagLambda = lambda stars, index: stars.LSSTMagZ[index]
            lsstMagNoATMLambda = lambda stars, index: stars.LSSTMagZNoATM[index]
        elif filter is BrightStarDatabase.FilterY:
            obsMagLambda = lambda stars, index: stars.ObsMagY[index]
            obsMagNewLambda = lambda stars, index: stars.ObsMagYNew[index]
            lsstMagLambda = lambda stars, index: stars.LSSTMagY[index]
            lsstMagNoATMLambda = lambda stars, index: stars.LSSTMagYNoATM[index]            
        
        lsstIndex, lsstNumberBelowCriteria, lsstNumberInCriteria, lsstNumberAboveCriteria, lsstNumberIgnored = self.processStarsInternal(stars, lowMagnitude, highMagnitude, maxDistance, False, lsstMagLambda)
        lsstNoAtmIndex, lsstNoAtmNumberBelowCriteria, lsstNoAtmNumberInCriteria, lsstNoAtmNumberAboveCriteria, lsstNoAtmNumberIgnored = self.processStarsInternal(stars, lowMagnitude, highMagnitude, maxDistance, False, lsstMagNoATMLambda)
        obsIndex, obsNumberBelowCriteria, obsNumberInCriteria, obsNumberAboveCriteria, obsNumberIgnored = self.processStarsInternal(stars, lowMagnitude, highMagnitude, maxDistance, True, obsMagLambda)
        obsNewIndex, obsNewNumberBelowCriteria, obsNewNumberInCriteria, obsNewNumberAboveCriteria, obsNewNumberIgnored = self.processStarsInternal(stars, lowMagnitude, highMagnitude, maxDistance, True, obsMagNewLambda)
        
        result = SkyCoverageResult()
        result.LSSTIndex += lsstIndex
        result.LSSTNumberBelowCriteria += lsstNumberBelowCriteria
        result.LSSTNumberInCriteria += lsstNumberInCriteria
        result.LSSTNumberAboveCriteria += lsstNumberAboveCriteria
        result.LSSTNumberIgnored += lsstNumberIgnored
        result.LSSTNoATMIndex += lsstNoAtmIndex
        result.LSSTNoATMNumberBelowCriteria += lsstNoAtmNumberBelowCriteria
        result.LSSTNoATMNumberInCriteria += lsstNoAtmNumberInCriteria
        result.LSSTNoATMNumberAboveCriteria += lsstNoAtmNumberAboveCriteria
        result.LSSTNoATMNumberIgnored += lsstNoAtmNumberIgnored
        result.ObsIndex += obsIndex
        result.ObsNumberBelowCriteria += obsNumberBelowCriteria
        result.ObsNumberInCriteria += obsNumberInCriteria
        result.ObsNumberAboveCriteria += obsNumberAboveCriteria
        result.ObsNumberIgnored += obsNumberIgnored
        result.ObsNewIndex += obsNewIndex
        result.ObsNewNumberBelowCriteria += obsNewNumberBelowCriteria
        result.ObsNewNumberInCriteria += obsNewNumberInCriteria
        result.ObsNewNumberAboveCriteria += obsNewNumberAboveCriteria
        result.ObsNewNumberIgnored += obsNewNumberIgnored
                                
        return result, obsMagLambda, obsMagNewLambda, lsstMagLambda, lsstMagNoATMLambda
        
    def processStarsInternal(self, stars, lowMagnitude, highMagnitude, maxDistance, ignoreNeg99, magnitudeLambda):
        """
        Takes a list of stars and determines which stars are candidates for wave front sensing by looking at their
        distance from the edge of the detector, and their magnitude.
        
        @param stars [in] The input set of stars that are on the detector and have had their *InMM fields populated.
        
        @param lowMagnitude [in] The minimum magnitude (magnitude that causes detector saturation).
        
        @param highMagnitude [in] The maximum magnitude (magnitude that is too dim to get good signal to noise).
        
        @param maxDistance [in] The maximum distance in mm to check around a candidate star.
        
        @param magnitudeLambda [in] The method used to grab the magnitude.
        """
        allStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in range(len(stars.RAInMM))]
        candidateStar = [index for index in range(len(stars.RAInMM)) if self.isCandidateStar(lowMagnitude, highMagnitude, maxDistance, stars.RAInPixel[index], stars.DeclInPixel[index], magnitudeLambda(stars, index))]
        candidateStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in candidateStar]
        indexResult = []
        numberBelowCriteriaResult = []
        numberInCriteriaResult = []
        numberAboveCriteriaResult = []
        numberIgnoredResult = []
        if len(candidateStarData) > 0:
            starDistances = scipy.spatial.distance.cdist(candidateStarData, allStarData)
            for candidateIndex in range(len(candidateStarData)):
                candidateDistances = starDistances[candidateIndex]
                numberBelowCriteria = 0
                numberInCriteria = -1
                numberAboveCriteria = 0
                numberIgnored = 0
                for index in range(len(allStarData)):
                    distance = candidateDistances[index]
                    magnitude = magnitudeLambda(stars, index)
                    if distance <= maxDistance:
                        if ignoreNeg99 and magnitude == -99:
                            numberIgnored += 1
                        elif magnitude < lowMagnitude:
                            numberBelowCriteria += 1
                        elif magnitude > highMagnitude:
                            numberAboveCriteria += 1
                        else:
                            numberInCriteria += 1

                indexResult.append(candidateStar[candidateIndex])
                numberBelowCriteriaResult.append(numberBelowCriteria)
                numberInCriteriaResult.append(numberInCriteria)
                numberAboveCriteriaResult.append(numberAboveCriteria)
                numberIgnoredResult.append(numberIgnored)
        return indexResult, numberBelowCriteriaResult, numberInCriteriaResult, numberAboveCriteriaResult, numberIgnoredResult

    def isCandidateStar(self, lowMagnitude, highMagnitude, maxDistance, raInPixel, declInPixel, mag):
        """
        Returns true if the candidate star is far enough away from the edge of the sensor and is in
        the proper magnitude range.
        
        @param lowMagnitude [in] The minimum magnitude (magnitude that causes detector saturation).
        
        @param highMagnitude [in] The maximum magnitude (magnitude that is too dim to get good signal to noise).
        
        @param maxDistance [in] The maximum distance in mm to check around a candidate star.
        
        @param raInPixel [in] The RA pixel coordinate of the star in question.
        
        @param declInPixel [in] The Decl pixel coordinate of the star in question.
        
        @param mag [in] The magnitude of the star in question.
        """
        maxDistanceInPixel = maxDistance / StarData.PixelSizeInMM
        return (raInPixel >= (MinRAPixel + maxDistanceInPixel) and raInPixel <= (MaxRAPixel - maxDistanceInPixel)) and \
            (declInPixel >= (MinDeclPixel + maxDistanceInPixel) and declInPixel <= (MaxDeclPixel - maxDistanceInPixel)) and \
            mag >= lowMagnitude and \
            mag <= highMagnitude
        
class SkyCoverageSurveyTest(unittest.TestCase):
    stars = None
    survey = None
    
    def setUp(self):
        self.stars = StarData.StarData([100, 200, 300], [1, 2, 3], [4, 5, 6], [7, 8, 9], [7, 8, 9])
        self.stars.populateDetector("Foobar")
        self.survey = SkyCoverageSurvey()
        
    def tearDown(self):
        self.stars = None
        self.survey = None
        
    def testNoCandidateStars(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 10, 10, 2.4)
        self.assertEqual(len(data.LSSTIndex), 0)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 0)
        self.assertEqual(len(data.LSSTNumberInCriteria), 0)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 0)

    def test1Bright(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        print self.stars.RAInPixel
        data = self.survey.processStars(self.stars, 8, 8, 2.4)
        self.assertEqual(len(data.LSSTIndex), 1)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 1)
        self.assertEqual(len(data.LSSTNumberInCriteria), 1)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 1)
        self.assertEqual(data.LSSTIndex[0], 1)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 1)
        self.assertEqual(data.LSSTNumberInCriteria[0], 0)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 0)
    
    def test2Bright(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 9, 9, 4)
        self.assertEqual(len(data.LSSTIndex), 1)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 1)
        self.assertEqual(len(data.LSSTNumberInCriteria), 1)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 1)
        self.assertEqual(data.LSSTIndex[0], 2)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 2)
        self.assertEqual(data.LSSTNumberInCriteria[0], 0)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 0)
    
    def test1Ok(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 8, 2.4)
        self.assertEqual(len(data.LSSTIndex), 2)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 2)
        self.assertEqual(len(data.LSSTNumberInCriteria), 2)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 2)
        self.assertEqual(data.LSSTIndex[0], 0)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 0)
        self.assertEqual(data.LSSTNumberInCriteria[0], 1)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 0)
        self.assertEqual(data.LSSTIndex[1], 1)
        self.assertEqual(data.LSSTNumberBelowCriteria[1], 0)
        self.assertEqual(data.LSSTNumberInCriteria[1], 1)
        self.assertEqual(data.LSSTNumberAboveCriteria[1], 0)
    
    def test2Ok(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 9, 4)
        self.assertEqual(len(data.LSSTIndex), 3)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 3)
        self.assertEqual(len(data.LSSTNumberInCriteria), 3)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 3)
        self.assertEqual(data.LSSTIndex[0], 0)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 0)
        self.assertEqual(data.LSSTNumberInCriteria[0], 2)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 0)
        self.assertEqual(data.LSSTIndex[1], 1)
        self.assertEqual(data.LSSTNumberBelowCriteria[1], 0)
        self.assertEqual(data.LSSTNumberInCriteria[1], 2)
        self.assertEqual(data.LSSTNumberAboveCriteria[1], 0)
        self.assertEqual(data.LSSTIndex[2], 2)
        self.assertEqual(data.LSSTNumberBelowCriteria[2], 0)
        self.assertEqual(data.LSSTNumberInCriteria[2], 2)
        self.assertEqual(data.LSSTNumberAboveCriteria[2], 0)
    
    def test1Dim(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 7, 2.4)
        self.assertEqual(len(data.LSSTIndex), 1)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 1)
        self.assertEqual(len(data.LSSTNumberInCriteria), 1)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 1)
        self.assertEqual(data.LSSTIndex[0], 0)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 0)
        self.assertEqual(data.LSSTNumberInCriteria[0], 0)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 1)

    def test2Dim(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 7, 4)
        self.assertEqual(len(data.LSSTIndex), 1)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 1)
        self.assertEqual(len(data.LSSTNumberInCriteria), 1)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 1)
        self.assertEqual(data.LSSTIndex[0], 0)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 0)
        self.assertEqual(data.LSSTNumberInCriteria[0], 0)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 2)
    
    def test1Bright1Ok(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 8, 9, 4)
        self.assertEqual(len(data.LSSTIndex), 2)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 2)
        self.assertEqual(len(data.LSSTNumberInCriteria), 2)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 2)
        self.assertEqual(data.LSSTIndex[0], 1)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 1)
        self.assertEqual(data.LSSTNumberInCriteria[0], 1)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 0)
        self.assertEqual(data.LSSTIndex[1], 2)
        self.assertEqual(data.LSSTNumberBelowCriteria[1], 1)
        self.assertEqual(data.LSSTNumberInCriteria[1], 1)
        self.assertEqual(data.LSSTNumberAboveCriteria[1], 0)
    
    def test1Ok1Dim(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 8, 4)
        self.assertEqual(len(data.LSSTIndex), 2)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 2)
        self.assertEqual(len(data.LSSTNumberInCriteria), 2)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 2)
        self.assertEqual(data.LSSTIndex[0], 0)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 0)
        self.assertEqual(data.LSSTNumberInCriteria[0], 1)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 1)
        self.assertEqual(data.LSSTIndex[1], 1)
        self.assertEqual(data.LSSTNumberBelowCriteria[1], 0)
        self.assertEqual(data.LSSTNumberInCriteria[1], 1)
        self.assertEqual(data.LSSTNumberAboveCriteria[1], 1)
   
    def test1Dim1Bright(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 8, 8, 4)
        self.assertEqual(len(data.LSSTIndex), 1)
        self.assertEqual(len(data.LSSTNumberBelowCriteria), 1)
        self.assertEqual(len(data.LSSTNumberInCriteria), 1)
        self.assertEqual(len(data.LSSTNumberAboveCriteria), 1)
        self.assertEqual(data.LSSTIndex[0], 1)
        self.assertEqual(data.LSSTNumberBelowCriteria[0], 1)
        self.assertEqual(data.LSSTNumberInCriteria[0], 0)
        self.assertEqual(data.LSSTNumberAboveCriteria[0], 1)

if __name__ == "__main__":
    unittest.main()