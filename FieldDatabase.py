import numpy

class FieldDatabase:
    __file = ""
    __acceptableRADecl = lambda x: True
    
    def __init__(self, file, acceptableRADecl):
        self.__file = file
        self.__acceptableRADecl = acceptableRADecl

    def getRADecl(self):
        rawData = numpy.loadtxt(self.__file)
        return [x[0] for x in rawData if self.__acceptableRADecl(x)], [x[1] for x in rawData if self.__acceptableRADecl(x)]

if __name__ == "__main__":
    ra, decl = FieldDatabase(".\Fields.txt", lambda x: x[1] <= 2 or (x[0] >= 0 and x[0] <= 12 and x[1] <= 30)).getRADecl()
    print "RA Number   : %s" % (len(ra) == 2782)
    print "RA Min      : %s" % (min(ra) == 0.0)
    print "RA Max      : %s" % (max(ra) == 358.475901)
    print "Decl Number : %s" % (len(decl) == 2782)
    print "Decl Min    : %s" % (min(decl) == -90.0)
    print "Decl Max    : %s" % (max(decl) == 29.407573)