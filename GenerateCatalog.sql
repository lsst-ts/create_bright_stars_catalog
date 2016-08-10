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
    `sed` CHAR(28) NOT NULL,
    `ebv` FLOAT NOT NULL,
    `lsstUNotAtm` FLOAT NOT NULL,
    `lsstGNotAtm` FLOAT NOT NULL,
    `lsstRNotAtm` FLOAT NOT NULL,
    `lsstINotAtm` FLOAT NOT NULL,
    `lsstZNotAtm` FLOAT NOT NULL,
    `lsstYNotAtm` FLOAT NOT NULL,
    `lsstU` FLOAT NOT NULL,
    `lsstG` FLOAT NOT NULL,
    `lsstR` FLOAT NOT NULL,
    `lsstI` FLOAT NOT NULL,
    `lsstZ` FLOAT NOT NULL,
    `lsstY` FLOAT NOT NULL,
    `sdssUExt` FLOAT NOT NULL,
    `sdssGExt` FLOAT NOT NULL,
    `sdssRExt` FLOAT NOT NULL,
    `sdssIExt` FLOAT NOT NULL,
    `sdssZExt` FLOAT NOT NULL,
    `sdssU` FLOAT NOT NULL,
    `sdssG` FLOAT NOT NULL,
    `sdssR` FLOAT NOT NULL,
    `sdssI` FLOAT NOT NULL,
    `sdssZ` FLOAT NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;

CREATE TABLE `FilteredCatalog`(
    `id` BIGINT UNSIGNED NOT NULL,
    `sourceFile` CHAR(5) NOT NULL,
    `starID` BIGINT UNSIGNED NOT NULL,
    `ra` DOUBLE NOT NULL,
    `decl` DOUBLE NOT NULL,
    `muRA` FLOAT NOT NULL,
    `muDecl` FLOAT NOT NULL,
    `sed` CHAR(28) NOT NULL,
    `ebv` FLOAT NOT NULL,
    `lsstUNotAtm` FLOAT NOT NULL,
    `lsstGNotAtm` FLOAT NOT NULL,
    `lsstRNotAtm` FLOAT NOT NULL,
    `lsstINotAtm` FLOAT NOT NULL,
    `lsstZNotAtm` FLOAT NOT NULL,
    `lsstYNotAtm` FLOAT NOT NULL,
    `lsstU` FLOAT NOT NULL,
    `lsstG` FLOAT NOT NULL,
    `lsstR` FLOAT NOT NULL,
    `lsstI` FLOAT NOT NULL,
    `lsstZ` FLOAT NOT NULL,
    `lsstY` FLOAT NOT NULL,
    `sdssUExt` FLOAT NOT NULL,
    `sdssGExt` FLOAT NOT NULL,
    `sdssRExt` FLOAT NOT NULL,
    `sdssIExt` FLOAT NOT NULL,
    `sdssZExt` FLOAT NOT NULL,
    `sdssU` FLOAT NOT NULL,
    `sdssG` FLOAT NOT NULL,
    `sdssR` FLOAT NOT NULL,
    `sdssI` FLOAT NOT NULL,
    `sdssZ` FLOAT NOT NULL,
    PRIMARY KEY(`id`)) ENGINE=MyISAM;

LOAD DATA LOCAL INFILE '/home/ccontaxis/brightstarraw.csv' INTO TABLE `Catalog`
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
(`sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `sed`, `ebv`, `lsstUNotAtm`, `lsstGNotAtm`, `lsstRNotAtm`, `lsstINotAtm`, `lsstZNotAtm`, `lsstYNotAtm`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `sdssUExt`, `sdssGExt`, `sdssRExt`, `sdssIExt`, `sdssZExt`, `sdssU`, `sdssG`, `sdssR`, `sdssI`, `sdssZ`);

INSERT INTO `FilteredCatalog` (`id`, `sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `sed`, `ebv`, `lsstUNotAtm`, `lsstGNotAtm`, `lsstRNotAtm`, `lsstINotAtm`, `lsstZNotAtm`, `lsstYNotAtm`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `sdssUExt`, `sdssGExt`, `sdssRExt`, `sdssIExt`, `sdssZExt`, `sdssU`, `sdssG`, `sdssR`, `sdssI`, `sdssZ`)
SELECT `id`, `sourceFile`, `starID`, `ra`, `decl`, `muRA`, `muDecl`, `sed`, `ebv`, `lsstUNotAtm`, `lsstGNotAtm`, `lsstRNotAtm`, `lsstINotAtm`, `lsstZNotAtm`, `lsstYNotAtm`, `lsstU`, `lsstG`, `lsstR`, `lsstI`, `lsstZ`, `lsstY`, `sdssUExt`, `sdssGExt`, `sdssRExt`, `sdssIExt`, `sdssZExt`, `sdssU`, `sdssG`, `sdssR`, `sdssI`, `sdssZ`
FROM `Catalog`
WHERE ((`decl` >= -90 AND `decl` <= 4) OR ((`ra` >= 358 OR `ra` <= 14) AND `decl` <= 32));
    
CREATE INDEX `DeclIndex` on `FilteredCatalog` (`decl`);
CREATE INDEX `RAIndex` on `FilteredCatalog` (`ra`);