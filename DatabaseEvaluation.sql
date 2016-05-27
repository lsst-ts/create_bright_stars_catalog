# This file contains the sql statements used to generate the bright star
# catalog database. The query list below can be used to quickly find a 
# specific query if it needs to be executed again. Just search for 
# "# x." where x is the number in the query list.
#
# Query list
# 1. Create the bright star catalog database and tables
# 2. Load data into the catalog
# 3. Create u, g, r, i, z, and y index on catalog
# 4. Load filtered data from catalog into u, g, r, i, z, and y catalogs
# 5. Create index on u, g, r, i, z, and y catalogs
# 6. Create filtered catalog table
# 7. Load filtered data from catalog into filtered catalog
# 8. Create u, g, r, i, z, and y index on filtered catalog
# 9. Optimize catalog tables
# 10. Create test index on UCatalog

# --------------------------------------------------------
# 1. Create the bright star catalog database and tables
# --------------------------------------------------------
CREATE DATABASE `BrightStarCatalog`;

USE `BrightStarCatalog`;

CREATE TABLE `Catalog`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `sourceFile` CHAR(5) NOT NULL,
    `starID` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `muRA` FLOAT NOT NULL,
    `muDecl` FLOAT NOT NULL,
    `magB` FLOAT NOT NULL,
    `magV` FLOAT NOT NULL,
    `magU` FLOAT NOT NULL,
    `magG` FLOAT NOT NULL,
    `magR` FLOAT NOT NULL,
    `magI` FLOAT NOT NULL,
    `magZ` FLOAT NOT NULL,
    `magY` FLOAT NOT NULL,
    `magJ` FLOAT NOT NULL,
    `magH` FLOAT NOT NULL,
    `magK` FLOAT NOT NULL,
    `w1` FLOAT NOT NULL,
    `w2` FLOAT NOT NULL,
    `w3` FLOAT NOT NULL,
    `w4` FLOAT NOT NULL,
    `magSST` FLOAT NOT NULL,
    `flag` INT NOT NULL,
    `lsstSED` CHAR(28) NOT NULL,
    `lsstU` FLOAT NOT NULL,
    `lsstG` FLOAT NOT NULL,
    `lsstR` FLOAT NOT NULL,
    `lsstI` FLOAT NOT NULL,
    `lsstZ` FLOAT NOT NULL,
    `lsstY` FLOAT NOT NULL,
    `lsstEBV` FLOAT NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;
    
CREATE TABLE `UCatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `mag` DOUBLE NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;
    
CREATE TABLE `GCatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `mag` DOUBLE NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;

CREATE TABLE `RCatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `mag` DOUBLE NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;

CREATE TABLE `ICatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `mag` DOUBLE NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;
    
CREATE TABLE `ZCatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `mag` DOUBLE NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;
        
CREATE TABLE `YCatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `mag` DOUBLE NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;
    
GRANT ALL PRIVILEGES ON `BrightStarCatalog`.* to `lsstwasadmin`@`localhost` WITH GRANT OPTION;

GRANT ALL PRIVILEGES ON `BrightStarCatalog`.* to `lsstwasadmin`@`rhea.lsst.org` WITH GRANT OPTION;

# --------------------------------------------------------
# 2. Load data into the catalog
# --------------------------------------------------------
LOAD DATA LOCAL INFILE '/home/ccontaxis/brightstarraw.csv' INTO TABLE `Catalog`
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
(`sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `magB`, `magV`, `magU`, `magG`, `magR`, `magI`, `magZ`, `magY`, `magJ`, `magH`, `magK`, `w1`, `w2`, `w3`, `w4`, `magSST`, `flag`, `lsstSED`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `lsstEBV`)
    
# --------------------------------------------------------
# 3. Create u, g, r, i, z, and y index on catalog
# --------------------------------------------------------
CREATE INDEX `UFilterIndex` ON `Catalog` (`lsstU` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `GFilterIndex` ON `Catalog` (`lsstG` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `RFilterIndex` ON `Catalog` (`lsstR` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `IFilterIndex` ON `Catalog` (`lsstI` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `ZFilterIndex` ON `Catalog` (`lsstZ` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `YFilterIndex` ON `Catalog` (`lsstY` ASC, `decl` ASC, `ra` ASC);
    
# --------------------------------------------------------
# 4. Load filtered data from catalog into u, g, r, i, z, and y catalogs
# --------------------------------------------------------
INSERT INTO `UCatalog` (`id`, `ra`, `decl`, `mag`)
SELECT `id`, `ra`, `decl`, `lsstU`
FROM `Catalog`
WHERE (`lsstU` >= 6.32 AND `lsstU` <= 16.68) AND
    ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));
    
INSERT INTO `GCatalog` (`id`, `ra`, `decl`, `mag`)
SELECT `id`, `ra`, `decl`, `lsstG`
FROM `Catalog`
WHERE (`lsstG` >= 8.12 AND `lsstG` <= 18.05) AND
    ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));
    
INSERT INTO `RCatalog` (`id`, `ra`, `decl`, `mag`)
SELECT `id`, `ra`, `decl`, `lsstR`
FROM `Catalog`
WHERE (`lsstR` >= 7.93 AND `lsstR` <= 17.61) AND
    ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));
    
INSERT INTO `ICatalog` (`id`, `ra`, `decl`, `mag`)
SELECT `id`, `ra`, `decl`, `lsstI`
FROM `Catalog`
WHERE (`lsstI` >= 7.60 AND `lsstI` <= 17.14) AND
    ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));
    
INSERT INTO `ZCatalog` (`id`, `ra`, `decl`, `mag`)
SELECT `id`, `ra`, `decl`, `lsstZ`
FROM `Catalog`
WHERE (`lsstZ` >= 7.21 AND `lsstZ` <= 15.68) AND
    ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));
    
INSERT INTO `YCatalog` (`id`, `ra`, `decl`, `mag`)
SELECT `id`, `ra`, `decl`, `lsstY`
FROM `Catalog`
WHERE (`lsstY` >= 6.39 AND `lsstY` <= 15.64) AND
    ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));

# --------------------------------------------------------
# 5. Create index on u, g, r, i, z, and y catalogs
# --------------------------------------------------------
CREATE INDEX `FilterIndex` ON `UCatalog` (`mag`, `decl`, `ra`);
CREATE INDEX `FilterIndex` ON `GCatalog` (`mag`, `decl`, `ra`);
CREATE INDEX `FilterIndex` ON `RCatalog` (`mag`, `decl`, `ra`);
CREATE INDEX `FilterIndex` ON `ICatalog` (`mag`, `decl`, `ra`);
CREATE INDEX `FilterIndex` ON `ZCatalog` (`mag`, `decl`, `ra`);
CREATE INDEX `FilterIndex` ON `YCatalog` (`mag`, `decl`, `ra`);

# --------------------------------------------------------
# 6. Create filtered catalog table
# --------------------------------------------------------
CREATE TABLE `FilteredCatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `sourceFile` CHAR(5) NOT NULL,
    `starID` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `muRA` FLOAT NOT NULL,
    `muDecl` FLOAT NOT NULL,
    `magB` FLOAT NOT NULL,
    `magV` FLOAT NOT NULL,
    `magU` FLOAT NOT NULL,
    `magG` FLOAT NOT NULL,
    `magR` FLOAT NOT NULL,
    `magI` FLOAT NOT NULL,
    `magZ` FLOAT NOT NULL,
    `magY` FLOAT NOT NULL,
    `magJ` FLOAT NOT NULL,
    `magH` FLOAT NOT NULL,
    `magK` FLOAT NOT NULL,
    `w1` FLOAT NOT NULL,
    `w2` FLOAT NOT NULL,
    `w3` FLOAT NOT NULL,
    `w4` FLOAT NOT NULL,
    `magSST` FLOAT NOT NULL,
    `flag` INT NOT NULL,
    `lsstSED` CHAR(28) NOT NULL,
    `lsstU` FLOAT NOT NULL,
    `lsstG` FLOAT NOT NULL,
    `lsstR` FLOAT NOT NULL,
    `lsstI` FLOAT NOT NULL,
    `lsstZ` FLOAT NOT NULL,
    `lsstY` FLOAT NOT NULL,
    `lsstEBV` FLOAT NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;
    
# --------------------------------------------------------
# 7. Load filtered data from catalog into filtered catalog
# --------------------------------------------------------
INSERT INTO `FilteredCatalog` (`id`, `sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `magB`, `magV`, `magU`, `magG`, `magR`, `magI`, `magZ`, `magY`, `magJ`, `magH`, `magK`, `w1`, `w2`, `w3`, `w4`, `magSST`, `flag`, `lsstSED`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `lsstEBV`)
SELECT `id`, `sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `magB`, `magV`, `magU`, `magG`, `magR`, `magI`, `magZ`, `magY`, `magJ`, `magH`, `magK`, `w1`, `w2`, `w3`, `w4`, `magSST`, `flag`, `lsstSED`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `lsstEBV`
FROM `Catalog`
WHERE ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));

# --------------------------------------------------------
# 8. Create u, g, r, i, z, and y index on filtered catalog
# --------------------------------------------------------
CREATE INDEX `UFilterIndex` ON `FilteredCatalog` (`lsstU` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `GFilterIndex` ON `FilteredCatalog` (`lsstG` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `RFilterIndex` ON `FilteredCatalog` (`lsstR` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `IFilterIndex` ON `FilteredCatalog` (`lsstI` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `ZFilterIndex` ON `FilteredCatalog` (`lsstZ` ASC, `decl` ASC, `ra` ASC);
CREATE INDEX `YFilterIndex` ON `FilteredCatalog` (`lsstY` ASC, `decl` ASC, `ra` ASC);

# --------------------------------------------------------
# 9. Optimize catalog tables
# --------------------------------------------------------
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog Catalog
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog FilteredCatalog
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog UCatalog
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog GCatalog
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog RCatalog
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog ICatalog
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog ZCatalog
mysqlcheck --optimize --user=lsstwasadmin --password=lsstwasadmin BrightStarCatalog YCatalog

# --------------------------------------------------------
# 10. Create test index on UCatalog
# --------------------------------------------------------
CREATE INDEX `TestIndex` ON `UCatalog` (`decl`);
CREATE INDEX `DecIndex` on `FilteredCatalog` (`decl`);
CREATE INDEX `RAIndex` on `FilteredCatalog` (`ra`);