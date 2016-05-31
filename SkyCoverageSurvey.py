import numpy
import scipy
import scipy.spatial
import StarData
import unittest

class SkyCoverageResult(object):
    def __init__(self):
        self.Index = []
        self.NumberBelowCriteria = []
        self.NumberInCriteria = []
        self.NumberAboveCriteria = []
    
class SkyCoverageSurvey(object):
    def processStars(self, stars, lowMagnitude, highMagnitude, maxDistance):
        allStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in range(len(stars.RAInMM))]
        canidateStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in range(len(stars.RAInMM)) if (stars.Mag[index] >= lowMagnitude and stars.Mag[index] <= highMagnitude)]
        canidateStar = [index for index in range(len(stars.RAInMM)) if (stars.Mag[index] >= lowMagnitude and stars.Mag[index] <= highMagnitude)]
        starDistances = scipy.spatial.distance.cdist(canidateStarData, allStarData)
        result = SkyCoverageResult()
        for canidateIndex in range(len(canidateStarData)):
            canidateDistances = starDistances[canidateIndex]
            numberBelowCriteria = 0
            numberInCriteria = -1
            numberAboveCriteria = 0
            for index in range(len(allStarData)):
                distance = canidateDistances[index]
                if distance <= maxDistance:
                    if stars.Mag[index] < lowMagnitude:
                        numberBelowCriteria += 1
                    elif stars.Mag[index] > highMagnitude:
                        numberAboveCriteria += 1
                    else:
                        numberInCriteria += 1

            result.Index.append(canidateStar[canidateIndex])
            result.NumberBelowCriteria.append(numberBelowCriteria)
            result.NumberInCriteria.append(numberInCriteria)
            result.NumberAboveCriteria.append(numberAboveCriteria)
        return result
        
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

    def test1Bright(self):
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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
        self.stars.populateRAData([x / StarData.PixelSizeInMM for x in [1, 2, 5]])
        self.stars.populateDeclData([x / StarData.PixelSizeInMM for x in [1, 3, 1]])
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