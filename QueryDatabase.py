import BrightStarDatabase

brightStarDatabaseHost = "140.252.32.27"
brightStarDatabasePort = 3306
brightStarDatabaseUser = "lsstwasadmin"
brightStarDatabasePassword = "lsstwasadmin"
brightStarDatabaseDatabase = "BrightStarCatalog"

filter = BrightStarDatabase.FilterU
corners = "17.362827	-88.494997	20.196462	-88.414581	11.872206	-88.327991	14.681893	-88.255307"
tokens = corners.split('\t')
corner1 = (float(tokens[0]), float(tokens[1]))
corner2 = (float(tokens[2]), float(tokens[3]))
corner3 = (float(tokens[4]), float(tokens[5]))
corner4 = (float(tokens[6]), float(tokens[7]))

def run(description, statement):
    print description
    for item in brightStarDatabase.general(statement):
        print item

try:
    # Connect to database
    brightStarDatabase = BrightStarDatabase.BrightStarDatabase()
    brightStarDatabase.connect(brightStarDatabaseHost, brightStarDatabasePort, brightStarDatabaseUser, brightStarDatabasePassword, brightStarDatabaseDatabase)
    
    #stars = brightStarDatabase.query(filter, corner1, corner2, corner3, corner4)
    #print "%s,%s,%s,%s" % ("RA", "Decl", "ObsMag", "LSSTMag")
    #for index in range(len(stars.ID)):
    #    print "%f,%f,%f,%f" % (stars.RA[index], stars.Decl[index], stars.ObsMag[index], stars.LSSSTMag[index])
        
    #for filter in ["U", "G", "R", "I", "Z", "Y"]:
    run(filter, "SELECT `sourceFile`, `lsstU` FROM `Catalog` WHERE `lsstU` > 50 LIMIT 10")    
    
finally:
    brightStarDatabase.disconnect()