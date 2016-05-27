import numpy
import scipy
import scipy.spatial
import StarData

class SkyCoverageResult:
    ID = []
    NumberBelowCriteria = []
    NumberInCriteria = []
    NumberAboveCriteria = []
    
class SkyCoverageSurvey:
    def processStars(self, stars, lowMagnitude, highMagnitude, maxDistance):
        allStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in range(len(stars.RAInMM))]
        canidateStarData = [[stars.RAInMM[index], stars.DeclInMM[index]] for index in range(len(stars.RAInMM)) if (stars.Mag[index] >= lowMagnitude and stars.Mag[index] <= highMagnitude)]
        canidateStar = [index for index in range(len(stars.RAInMM)) if (stars.Mag[index] >= lowMagnitude and stars.Mag[index] <= highMagnitude)]
        starDistances = scipy.spatial.distance.cdist(canidateStarData, allStarData)
        result = SkyCoverageResult()
        for canidateIndex in range(len(canidateStarData)):
            canidateDistances = starDistances[canidateIndex]
            numberBelowCriteria = 0
            numberInCriteria = 0
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

            result.ID.append(stars.ID[canidateStar[canidateIndex]])
            result.NumberBelowCriteria.append(numberBelowCriteria)
            result.NumberInCriteria.append(numberInCriteria)
            result.NumberAboveCriteria.append(numberAboveCriteria)
            
        return result

if __name__ == "__main__":
    stars = StarData.StarData([100, 200, 300], [1, 2, 3], [4, 5, 6], [7, 8, 9])
    stars.populateDetector("Foobar")
    stars.populateRAData([10, 20, 33])
    stars.populateDeclData([40, 50, 63])
    
    survey = SkyCoverageSurvey()
    data = survey.processStars(stars, 8, 8, 0.0022)
    print "ID     : %s" % data.ID
    print "BRIGHT : %s" % data.NumberBelowCriteria
    print "OK     : %s" % data.NumberInCriteria
    print "DIM    : %s" % data.NumberAboveCriteria