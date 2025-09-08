CREATE DATABASE SE521;

CREATE TABLE SE521.tempratures (
  `DateTm` datetime NOT NULL,
  `tc1` float DEFAULT NULL,
  `tc2` float DEFAULT NULL,
  `tc3` float DEFAULT NULL,
  `tc4` float DEFAULT NULL,
  PRIMARY KEY (`DateTm`)
) ENGINE=MyISAM  COMMENT='Data recorded by SE521 temperature logging equipment.';
