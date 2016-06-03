import numpy
import scipy
import scipy.spatial
import StarData
import unittest

MinRAPixel = 0
MaxRAPixel = 4095
MinDeclPixel = 0
MaxDeclPixel = 2047

class SkyCoverageResult(object):
    def __init__(self):
        self.Index = []
        self.NumberBelowCriteria = []
        self.NumberInCriteria = []
        self.NumberAboveCriteria = []
    
class SkyCoverageSurvey(object):
    def processStars(self, stars, lowMagnitude, highMagnitude, maxDistance):
        """
        Takes a list of stars and determines which stars are candidates for wave front sensing by looking at their
        distance from the edge of the detector, and their magnitude.
        
        @param stars [in] The input set of stars that are on the detector and have had their *InMM fields populated.
        
        @param lowMagnitude [in] The minimum magnitude (magnitude that causes detector saturation).
        
        @param highMagnitude [in] The maximum magnitude (magnitude that is too dim to get good signal to noise).
        
        @param maxDistance [in] The maximum distance in mm to check around a candidate star.
        """
        allStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in range(len(stars.RAInMM))]
        candidateStar = [index for index in range(len(stars.RAInMM)) if self.isCandidateStar(lowMagnitude, highMagnitude, maxDistance, stars.RAInPixel[index], stars.DeclInPixel[index], stars.Mag[index])]
        candidateStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in candidateStar]
        result = SkyCoverageResult()
        if len(candidateStarData) > 0:
            starDistances = scipy.spatial.distance.cdist(candidateStarData, allStarData)
            for candidateIndex in range(len(candidateStarData)):
                candidateDistances = starDistances[candidateIndex]
                numberBelowCriteria = 0
                numberInCriteria = -1
                numberAboveCriteria = 0
                for index in range(len(allStarData)):
                    distance = candidateDistances[index]
                    if distance <= maxDistance:
                        if stars.Mag[index] < lowMagnitude:
                            numberBelowCriteria += 1
                        elif stars.Mag[index] > highMagnitude:
                            numberAboveCriteria += 1
                        else:
                            numberInCriteria += 1

                result.Index.append(candidateStar[candidateIndex])
                result.NumberBelowCriteria.append(numberBelowCriteria)
                result.NumberInCriteria.append(numberInCriteria)
                result.NumberAboveCriteria.append(numberAboveCriteria)
        return result
        
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
        self.stars = StarData.StarData([100, 200, 300], [1, 2, 3], [4, 5, 6], [7, 8, 9])
        self.stars.populateDetector("Foobar")
        self.survey = SkyCoverageSurvey()
        
    def tearDown(self):
        self.stars = None
        self.survey = None
        
    def testNoCandidateStars(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 10, 10, 2.4)
        self.assertEqual(len(data.Index), 0)
        self.assertEqual(len(data.NumberBelowCriteria), 0)
        self.assertEqual(len(data.NumberInCriteria), 0)
        self.assertEqual(len(data.NumberAboveCriteria), 0)

    def test1Bright(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        print self.stars.RAInPixel
        data = self.survey.processStars(self.stars, 8, 8, 2.4)
        self.assertEqual(len(data.Index), 1)
        self.assertEqual(len(data.NumberBelowCriteria), 1)
        self.assertEqual(len(data.NumberInCriteria), 1)
        self.assertEqual(len(data.NumberAboveCriteria), 1)
        self.assertEqual(data.Index[0], 1)
        self.assertEqual(data.NumberBelowCriteria[0], 1)
        self.assertEqual(data.NumberInCriteria[0], 0)
        self.assertEqual(data.NumberAboveCriteria[0], 0)
    
    def test2Bright(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 9, 9, 4)
        self.assertEqual(len(data.Index), 1)
        self.assertEqual(len(data.NumberBelowCriteria), 1)
        self.assertEqual(len(data.NumberInCriteria), 1)
        self.assertEqual(len(data.NumberAboveCriteria), 1)
        self.assertEqual(data.Index[0], 2)
        self.assertEqual(data.NumberBelowCriteria[0], 2)
        self.assertEqual(data.NumberInCriteria[0], 0)
        self.assertEqual(data.NumberAboveCriteria[0], 0)
    
    def test1Ok(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 8, 2.4)
        self.assertEqual(len(data.Index), 2)
        self.assertEqual(len(data.NumberBelowCriteria), 2)
        self.assertEqual(len(data.NumberInCriteria), 2)
        self.assertEqual(len(data.NumberAboveCriteria), 2)
        self.assertEqual(data.Index[0], 0)
        self.assertEqual(data.NumberBelowCriteria[0], 0)
        self.assertEqual(data.NumberInCriteria[0], 1)
        self.assertEqual(data.NumberAboveCriteria[0], 0)
        self.assertEqual(data.Index[1], 1)
        self.assertEqual(data.NumberBelowCriteria[1], 0)
        self.assertEqual(data.NumberInCriteria[1], 1)
        self.assertEqual(data.NumberAboveCriteria[1], 0)
    
    def test2Ok(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 9, 4)
        self.assertEqual(len(data.Index), 3)
        self.assertEqual(len(data.NumberBelowCriteria), 3)
        self.assertEqual(len(data.NumberInCriteria), 3)
        self.assertEqual(len(data.NumberAboveCriteria), 3)
        self.assertEqual(data.Index[0], 0)
        self.assertEqual(data.NumberBelowCriteria[0], 0)
        self.assertEqual(data.NumberInCriteria[0], 2)
        self.assertEqual(data.NumberAboveCriteria[0], 0)
        self.assertEqual(data.Index[1], 1)
        self.assertEqual(data.NumberBelowCriteria[1], 0)
        self.assertEqual(data.NumberInCriteria[1], 2)
        self.assertEqual(data.NumberAboveCriteria[1], 0)
        self.assertEqual(data.Index[2], 2)
        self.assertEqual(data.NumberBelowCriteria[2], 0)
        self.assertEqual(data.NumberInCriteria[2], 2)
        self.assertEqual(data.NumberAboveCriteria[2], 0)
    
    def test1Dim(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 7, 2.4)
        self.assertEqual(len(data.Index), 1)
        self.assertEqual(len(data.NumberBelowCriteria), 1)
        self.assertEqual(len(data.NumberInCriteria), 1)
        self.assertEqual(len(data.NumberAboveCriteria), 1)
        self.assertEqual(data.Index[0], 0)
        self.assertEqual(data.NumberBelowCriteria[0], 0)
        self.assertEqual(data.NumberInCriteria[0], 0)
        self.assertEqual(data.NumberAboveCriteria[0], 1)

    def test2Dim(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 7, 4)
        self.assertEqual(len(data.Index), 1)
        self.assertEqual(len(data.NumberBelowCriteria), 1)
        self.assertEqual(len(data.NumberInCriteria), 1)
        self.assertEqual(len(data.NumberAboveCriteria), 1)
        self.assertEqual(data.Index[0], 0)
        self.assertEqual(data.NumberBelowCriteria[0], 0)
        self.assertEqual(data.NumberInCriteria[0], 0)
        self.assertEqual(data.NumberAboveCriteria[0], 2)
    
    def test1Bright1Ok(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 8, 9, 4)
        self.assertEqual(len(data.Index), 2)
        self.assertEqual(len(data.NumberBelowCriteria), 2)
        self.assertEqual(len(data.NumberInCriteria), 2)
        self.assertEqual(len(data.NumberAboveCriteria), 2)
        self.assertEqual(data.Index[0], 1)
        self.assertEqual(data.NumberBelowCriteria[0], 1)
        self.assertEqual(data.NumberInCriteria[0], 1)
        self.assertEqual(data.NumberAboveCriteria[0], 0)
        self.assertEqual(data.Index[1], 2)
        self.assertEqual(data.NumberBelowCriteria[1], 1)
        self.assertEqual(data.NumberInCriteria[1], 1)
        self.assertEqual(data.NumberAboveCriteria[1], 0)
    
    def test1Ok1Dim(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 7, 8, 4)
        self.assertEqual(len(data.Index), 2)
        self.assertEqual(len(data.NumberBelowCriteria), 2)
        self.assertEqual(len(data.NumberInCriteria), 2)
        self.assertEqual(len(data.NumberAboveCriteria), 2)
        self.assertEqual(data.Index[0], 0)
        self.assertEqual(data.NumberBelowCriteria[0], 0)
        self.assertEqual(data.NumberInCriteria[0], 1)
        self.assertEqual(data.NumberAboveCriteria[0], 1)
        self.assertEqual(data.Index[1], 1)
        self.assertEqual(data.NumberBelowCriteria[1], 0)
        self.assertEqual(data.NumberInCriteria[1], 1)
        self.assertEqual(data.NumberAboveCriteria[1], 1)
   
    def test1Dim1Bright(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [11, 12, 15]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [11, 13, 11]])
        data = self.survey.processStars(self.stars, 8, 8, 4)
        self.assertEqual(len(data.Index), 1)
        self.assertEqual(len(data.NumberBelowCriteria), 1)
        self.assertEqual(len(data.NumberInCriteria), 1)
        self.assertEqual(len(data.NumberAboveCriteria), 1)
        self.assertEqual(data.Index[0], 1)
        self.assertEqual(data.NumberBelowCriteria[0], 1)
        self.assertEqual(data.NumberInCriteria[0], 0)
        self.assertEqual(data.NumberAboveCriteria[0], 1)

if __name__ == "__main__":
    unittest.main()