import numpy
import unittest

class FieldDatabase(object):
    def __init__(self, file, acceptableRADecl):
        self.__file = file
        self.__acceptableRADecl = acceptableRADecl

    def getRADecl(self):
        rawData = numpy.loadtxt(self.__file)
        return [x[0] for x in rawData if self.__acceptableRADecl(x)], [x[1] for x in rawData if self.__acceptableRADecl(x)]
        
class FieldDatabaseTest(unittest.TestCase):
    def testConstructor(self):
        ra, decl = FieldDatabase(".\Fields.txt", lambda x: x[1] <= 2 or (x[0] >= 0 and x[0] <= 12 and x[1] <= 30)).getRADecl()
        self.assertEqual(len(ra), 2782)
        self.assertEqual(min(ra), 0.0)
        self.assertEqual(max(ra), 358.475901)
        self.assertEqual(len(decl), 2782)
        self.assertEqual(min(decl), -90.0)
        self.assertEqual(max(decl), 29.407573)

if __name__ == "__main__":
    unittest.main()