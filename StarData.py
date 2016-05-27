PixelSizeInMM = 0.00015

class StarData:
    Detector = ""
    ID = []
    RA = []
    RAInPixel = []
    RAInMM = []
    Decl = []
    DeclInPixel = []
    DeclInMM = []
    Mag = []
    
    def __init__(self, id, ra, decl, mag):
        self.ID = id
        self.RA = ra
        self.Decl = decl
        self.Mag = mag
        
    def populateDetector(self, detector):
        self.Detector = detector
        
    def populateRAData(self, raInPixel):
        self.RAInPixel = raInPixel
        self.RAInMM = [x * PixelSizeInMM for x in self.RAInPixel]
        
    def populateDeclData(self, declInPixel):
        self.DeclInPixel = declInPixel
        self.DeclInMM = [x * PixelSizeInMM for x in self.DeclInPixel]
        
if __name__ == "__main__":
    stars = StarData([100, 200, 300], [1, 2, 3], [4, 5, 6], [7, 8, 9])
    stars.populateDetector("Foobar")
    stars.populateRAData([10, 20, 30])
    stars.populateDeclData([40, 50, 60])
    
    print "Detector       : %s" % (stars.Detector == "Foobar")
    print "ID[0]          : %s" % (stars.ID[0] == 100)
    print "ID[1]          : %s" % (stars.ID[1] == 200)
    print "ID[2]          : %s" % (stars.ID[2] == 300)
    print "RA[0]          : %s" % (stars.RA[0] == 1)
    print "RA[1]          : %s" % (stars.RA[1] == 2)
    print "RA[2]          : %s" % (stars.RA[2] == 3)
    print "RAInPixel[0]   : %s" % (stars.RAInPixel[0] == 10)
    print "RAInPixel[1]   : %s" % (stars.RAInPixel[1] == 20)
    print "RAInPixel[2]   : %s" % (stars.RAInPixel[2] == 30)
    print "RAInMM[0]      : %s" % (stars.RAInMM[0] == 10 * PixelSizeInMM)
    print "RAInMM[1]      : %s" % (stars.RAInMM[1] == 20 * PixelSizeInMM)
    print "RAInMM[2]      : %s" % (stars.RAInMM[2] == 30 * PixelSizeInMM)
    print "Decl[0]        : %s" % (stars.Decl[0] == 4)
    print "Decl[1]        : %s" % (stars.Decl[1] == 5)
    print "Decl[2]        : %s" % (stars.Decl[2] == 6)
    print "DeclInPixel[0] : %s" % (stars.DeclInPixel[0] == 40)
    print "DeclInPixel[1] : %s" % (stars.DeclInPixel[1] == 50)
    print "DeclInPixel[2] : %s" % (stars.DeclInPixel[2] == 60)
    print "DeclInMM[0]    : %s" % (stars.DeclInMM[0] == 40 * PixelSizeInMM)
    print "DeclInMM[1]    : %s" % (stars.DeclInMM[1] == 50 * PixelSizeInMM)
    print "DeclInMM[2]    : %s" % (stars.DeclInMM[2] == 60 * PixelSizeInMM)
    print "Mag[0]         : %s" % (stars.Mag[0] == 7)
    print "Mag[1]         : %s" % (stars.Mag[1] == 8)
    print "Mag[2]         : %s" % (stars.Mag[2] == 9)