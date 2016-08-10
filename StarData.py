import unittest

PixelSizeInMM = 0.01

class StarData(object):
    def __init__(self, ra, decl, obsMag, obsMagNew, lsstMag, lsstMagNoATM):
        self.Detector = "" 
        self.RA = ra
        self.RAInPixel = []
        self.RAInMM = []
        self.Decl = decl
        self.DeclInPixel = []
        self.DeclInMM = []
        self.ObsMag = obsMag
        self.ObsMagNew = obsMagNew
        self.LSSTMag = lsstMag
        self.LSSTMagNoATM = lsstMagNoATM
        
    def populateDetector(self, detector):
        """
        Populates the detector information for this set of stars.
        
        @param detector [in] The name of the detector.
        """
        self.Detector = detector
        
    def populateRAData(self, raInPixel):
        """
        Populates the RA pixel and mm data for this set of stars.
        
        @param raInPixel [in] The ra pixel coordinate each star falls on the detector.
        """
        self.RAInPixel = raInPixel
        self.RAInMM = [x * PixelSizeInMM for x in self.RAInPixel]
        
    def populateDeclData(self, declInPixel):
        """
        Populates the Decl pixel and mm data for this set of stars.
        
        @param declInPixel [in] The decl pixel coordinate each star falls on the detector.
        """
        self.DeclInPixel = declInPixel
        self.DeclInMM = [x * PixelSizeInMM for x in self.DeclInPixel]
        
class StarDataTest(unittest.TestCase):
    stars = None
    
    def setUp(self):
        self.stars = StarData([1, 2, 3], [4, 5, 6], [10, 11, 12], [16, 17, 18], [7, 8, 9], [13, 14, 15])

    def testConstructor(self):
        self.assertEqual(self.stars.RA[0], 1)
        self.assertEqual(self.stars.RA[1], 2)
        self.assertEqual(self.stars.RA[2], 3)
        self.assertEqual(self.stars.Decl[0], 4)
        self.assertEqual(self.stars.Decl[1], 5)
        self.assertEqual(self.stars.Decl[2], 6)
        self.assertEqual(self.stars.LSSTMag[0], 7)
        self.assertEqual(self.stars.LSSTMag[1], 8)
        self.assertEqual(self.stars.LSSTMag[2], 9)
        self.assertEqual(self.stars.ObsMag[0], 10)
        self.assertEqual(self.stars.ObsMag[1], 11)
        self.assertEqual(self.stars.ObsMag[2], 12)
        self.assertEqual(self.stars.LSSTMagNoATM[0], 13)
        self.assertEqual(self.stars.LSSTMagNoATM[1], 14)
        self.assertEqual(self.stars.LSSTMagNoATM[2], 15)
        self.assertEqual(self.stars.ObsMagNew[0], 16)
        self.assertEqual(self.stars.ObsMagNew[1], 17)
        self.assertEqual(self.stars.ObsMagNew[2], 18)
        
    def testDetector(self):
        self.stars.populateDetector("Foobar")
        self.assertEqual(self.stars.Detector, "Foobar")
    
    def testRAData(self):
        self.stars.populateRAData([10, 20, 30])
        self.assertEqual(self.stars.RAInPixel[0], 10)
        self.assertEqual(self.stars.RAInPixel[1], 20)
        self.assertEqual(self.stars.RAInPixel[2], 30)
        self.assertEqual(self.stars.RAInMM[0], 10 * PixelSizeInMM)
        self.assertEqual(self.stars.RAInMM[1], 20 * PixelSizeInMM)
        self.assertEqual(self.stars.RAInMM[2], 30 * PixelSizeInMM)
    
    def testDeclData(self):
        self.stars.populateDeclData([40, 50, 60])
        self.assertEqual(self.stars.DeclInPixel[0], 40)
        self.assertEqual(self.stars.DeclInPixel[1], 50)
        self.assertEqual(self.stars.DeclInPixel[2], 60)
        self.assertEqual(self.stars.DeclInMM[0], 40 * PixelSizeInMM)
        self.assertEqual(self.stars.DeclInMM[1], 50 * PixelSizeInMM)
        self.assertEqual(self.stars.DeclInMM[2], 60 * PixelSizeInMM)
        
if __name__ == "__main__":
    unittest.main()