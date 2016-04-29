# MariaDB [WFSCatalog]> select min(ra), max(ra), min(decl), max(decl) from BrightStars;
# +---------+------------+------------+-----------+
# | min(ra) | max(ra)    | min(decl)  | max(decl) |
# +---------+------------+------------+-----------+
# |       0 | 359.999999 | -89.988876 | 89.990081 |
# +---------+------------+------------+-----------+
# 1 row in set (0.01 sec)
#
#  Step 1
#    a) Select RA all, DEC -90 to +2
# 	but we need padding so everything less than +4
#       Select DEC <= 4
#
#    b) Select RA 0 to 12, DEC +2 to +30
#         but we need padding
#       Select RA >= 358 or RA <= 14
#       Select DEC > 4 and DEC <= 32


# CREATE TABLE `BrightStarsLSST` (
#   `brightStarID` bigint(16) NOT NULL AUTO_INCREMENT,
#   `starID` bigint(16) DEFAULT NULL,
#   `ra` double DEFAULT NULL,
#   `decl` double DEFAULT NULL,
#   `muRA` double DEFAULT NULL,
#   `muDecl` double DEFAULT NULL,
#   `magB` double DEFAULT NULL,
#   `magV` double DEFAULT NULL,
#   `magU` double DEFAULT NULL,
#   `magG` double DEFAULT NULL,
#   `magR` double DEFAULT NULL,
#   `magI` double DEFAULT NULL,
#   `magZ` double DEFAULT NULL,
#   `magY` double DEFAULT NULL,
#   `magJ` double DEFAULT NULL,
#   `magH` double DEFAULT NULL,
#   `magK` double DEFAULT NULL,
#   `w1` double DEFAULT NULL,
#   `w2` double DEFAULT NULL,
#   `w3` double DEFAULT NULL,
#   `w4` double DEFAULT NULL,
#   `magSST` double DEFAULT NULL,
#   `flag` double DEFAULT NULL,
#   PRIMARY KEY (`brightStarID`),
#   UNIQUE KEY `brightStarID_UNIQUE` (`brightStarID`),
#   KEY `ra` (`ra`),
#   KEY `decl` (`decl`)
# ) ENGINE=MyISAM DEFAULT CHARSET=big5;



import pymysql

HOST = "localhost"
USER = "lsstwasadmin"
PASSWD = "lsstwasadmin"
DB = "WFSCatalog"
PORT = 3306

if __name__ == "__main__" :
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB)
    cur_read = conn.cursor()
    cur_write = conn.cursor()

    # Figured out this number before
    TOTAL_ROWS = 391013801
    CHUNK_SIZE = 100000
    CHUNKS = (TOTAL_ROWS / CHUNK_SIZE) + 1
    print "Doing Step 1 a)"
    for i in range(CHUNKS):
        sql = "select * from BrightStars where decl <=4 limit %d,%d" % (i*CHUNK_SIZE, CHUNK_SIZE)
        cur_read.execute(sql)
        print "read %d/%d chunks" % (i, CHUNKS)

        for row in cur_read :
            sql = "insert into BrightStarsLSST values %s" % str(row)
            cur_write.execute(sql)
        print "wrote %d/%d chunks" % (i, CHUNKS)

    TOTAL_ROWS = 1221231
    CHUNKS = (TOTAL_ROWS / CHUNK_SIZE) + 1
    print "Doing Step 1 b)"
    for i in range(CHUNKS) :
        sql = "select count(*) from BrightStars where (ra >= 358 or ra <=14) and (decl > 4 and decl <= 32) limit %d,%d" % (i*CHUNK_SIZE, CHUNK_SIZE);
        cur_read.execute(sql)
        print "read %d/%d chunks" % (i, CHUNKS)

        for row in cur_read :
            sql = "insert into BrightStarsLSST values %s" % str(row)
            cur_write.execute(sql)
        print "wrote %d/%d chunks" % (i, CHUNKS)

    cur_read.close()
    cur_write.close()
    conn.close()
