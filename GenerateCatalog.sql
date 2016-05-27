DROP DATABASE IF EXISTS `BrightStarCatalog`;

CREATE DATABASE `BrightStarCatalog`;

USE `BrightStarCatalog`;

GRANT ALL PRIVILEGES ON `BrightStarCatalog`.* to `lsstwasadmin`@`localhost` WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `BrightStarCatalog`.* to `lsstwasadmin`@`rhea.lsst.org` WITH GRANT OPTION;

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

LOAD DATA LOCAL INFILE '/home/ccontaxis/brightstarraw.csv' INTO TABLE `Catalog`
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
(`sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `magB`, `magV`, `magU`, `magG`, `magR`, `magI`, `magZ`, `magY`, `magJ`, `magH`, `magK`, `w1`, `w2`, `w3`, `w4`, `magSST`, `flag`, `lsstSED`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `lsstEBV`);

INSERT INTO `FilteredCatalog` (`id`, `sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `magB`, `magV`, `magU`, `magG`, `magR`, `magI`, `magZ`, `magY`, `magJ`, `magH`, `magK`, `w1`, `w2`, `w3`, `w4`, `magSST`, `flag`, `lsstSED`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `lsstEBV`)
SELECT `id`, `sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `magB`, `magV`, `magU`, `magG`, `magR`, `magI`, `magZ`, `magY`, `magJ`, `magH`, `magK`, `w1`, `w2`, `w3`, `w4`, `magSST`, `flag`, `lsstSED`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `lsstEBV`
FROM `Catalog`
WHERE ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));
    
CREATE INDEX `DeclIndex` on `FilteredCatalog` (`decl`);
CREATE INDEX `RAIndex` on `FilteredCatalog` (`ra`);