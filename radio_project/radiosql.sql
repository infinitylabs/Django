SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `radio_main` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `radio_main` ;

-- Altering tables at top so we can cry when you don't LISTEN
ALTER TABLE auth_group ENGINE=InnoDB;
ALTER TABLE auth_group_permissions ENGINE=InnoDB;
ALTER TABLE auth_message ENGINE=InnoDB;
ALTER TABLE auth_permission ENGINE=InnoDB;
ALTER TABLE auth_user ENGINE=InnoDB;
ALTER TABLE auth_user_groups ENGINE=InnoDB;
ALTER TABLE auth_user_user_permissions ENGINE=InnoDB;
ALTER TABLE django_content_type ENGINE=InnoDB;
ALTER TABLE django_session ENGINE=InnoDB;
ALTER TABLE django_site ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `radio_main`.`djs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`djs` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`djs` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NOT NULL ,
  `description` TEXT NULL ,
  `image` TEXT NULL ,
  `visible` TINYINT(1) NOT NULL DEFAULT 0 ,
  `priority` INT(12) NOT NULL DEFAULT 200 ,
  `user` INT(12) NOT NULL ,
  `theme` VARCHAR(60) NOT NULL DEFAULT 'default' ,
  PRIMARY KEY (`id`, `user`) ,
  CONSTRAINT `fk_djs_auth_user`
    FOREIGN KEY (`user` )
    REFERENCES `radio_main`.`auth_user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE INDEX `fk_djs_auth_user` ON `radio_main`.`djs` (`user` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`news`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`news` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`news` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `title` VARCHAR(45) NOT NULL ,
  `time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  `text` TEXT NOT NULL ,
  `commenting` TINYINT(1) NOT NULL DEFAULT 1 ,
  `poster` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `poster`) ,
  CONSTRAINT `fk_news_auth_user1`
    FOREIGN KEY (`poster` )
    REFERENCES `radio_main`.`auth_user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE INDEX `fk_news_auth_user1` ON `radio_main`.`news` (`poster` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`news_comments`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`news_comments` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`news_comments` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `news_id` INT(12) NOT NULL ,
  `nickname` VARCHAR(100) NULL DEFAULT 'Anonymous' ,
  `text` TEXT NOT NULL ,
  `mail` VARCHAR(200) NULL ,
  `poster` INT(12) NULL ,
  `time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  PRIMARY KEY (`id`, `news_id`) ,
  CONSTRAINT `fk_news_comments_news1`
    FOREIGN KEY (`news_id` )
    REFERENCES `radio_main`.`news` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_news_comments_auth_user1`
    FOREIGN KEY (`poster` )
    REFERENCES `radio_main`.`auth_user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE INDEX `fk_news_comments_news1` ON `radio_main`.`news_comments` (`news_id` ASC) ;

CREATE INDEX `fk_news_comments_users1` ON `radio_main`.`news_comments` (`poster` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`track`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`track` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`track` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `metadata` VARCHAR(400) NOT NULL ,
  `length` INT(12) NULL DEFAULT 0 ,
  `hash` VARCHAR(45) NOT NULL DEFAULT '' ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB
ROW_FORMAT = COMPRESSED;

CREATE UNIQUE INDEX `hash_UNIQUE` ON `radio_main`.`track` (`hash` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`songs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`songs` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`songs` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `hash` VARCHAR(45) NOT NULL ,
  `track_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_songs_track1`
    FOREIGN KEY (`track_id` )
    REFERENCES `radio_main`.`track` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE UNIQUE INDEX `hash_UNIQUE` ON `radio_main`.`songs` (`hash` ASC) ;

CREATE INDEX `fk_songs_track1` ON `radio_main`.`songs` (`track_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`collection`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`collection` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`collection` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `songs_id` INT(12) NOT NULL ,
  `usable` TINYINT(1) NOT NULL DEFAULT 0 ,
  `filename` TEXT NULL ,
  `good_upload` TINYINT(1) NOT NULL DEFAULT 0 ,
  `need_reupload` TINYINT(1) NOT NULL DEFAULT 0 ,
  `popularity` INT(12) NOT NULL DEFAULT 0 ,
  `status` TINYINT(1) NOT NULL DEFAULT 0 ,
  `decline_reason` VARCHAR(120) NOT NULL DEFAULT '' ,
  `comment` VARCHAR(120) NOT NULL DEFAULT '' ,
  `original_filename` VARCHAR(200) NOT NULL DEFAULT '' ,
  PRIMARY KEY (`id`, `songs_id`) ,
  CONSTRAINT `fk_collection_songs1`
    FOREIGN KEY (`songs_id` )
    REFERENCES `radio_main`.`songs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE INDEX `fk_collection_songs1` ON `radio_main`.`collection` (`songs_id` ASC) ;

CREATE UNIQUE INDEX `songs_id_UNIQUE` ON `radio_main`.`collection` (`songs_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`players`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`players` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`players` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NULL ,
  `useragent` VARCHAR(200) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;

CREATE UNIQUE INDEX `useragent_UNIQUE` ON `radio_main`.`players` (`useragent` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`hostnames`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`hostnames` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`hostnames` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `hostname` VARCHAR(150) NOT NULL DEFAULT '' ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `radio_main`.`nicknames`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`nicknames` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`nicknames` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `nick` VARCHAR(30) NULL ,
  `passcode` VARCHAR(8) NULL ,
  `hostnames_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `hostnames_id`) ,
  CONSTRAINT `fk_nicknames_hostnames1`
    FOREIGN KEY (`hostnames_id` )
    REFERENCES `radio_main`.`hostnames` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `nick_UNIQUE` ON `radio_main`.`nicknames` (`nick` ASC) ;

CREATE INDEX `fk_nicknames_hostnames1` ON `radio_main`.`nicknames` (`hostnames_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`listeners`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`listeners` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`listeners` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `ip` VARCHAR(50) NULL DEFAULT '' ,
  `players_id` INT(12) NULL ,
  `banned` TINYINT(1) NOT NULL DEFAULT 0 ,
  `last_seen` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
  `nicknames_id` INT(12) NULL ,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_listeners_players1`
    FOREIGN KEY (`players_id` )
    REFERENCES `radio_main`.`players` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_listeners_nicknames1`
    FOREIGN KEY (`nicknames_id` )
    REFERENCES `radio_main`.`nicknames` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_listeners_players1` ON `radio_main`.`listeners` (`players_id` ASC) ;

CREATE UNIQUE INDEX `ip_UNIQUE` ON `radio_main`.`listeners` (`ip` ASC) ;

CREATE INDEX `fk_listeners_nicknames1` ON `radio_main`.`listeners` (`nicknames_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`requests`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`requests` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`requests` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ,
  `songs_id` INT(12) NOT NULL ,
  `listeners_id` INT(12) NOT NULL ,
  `hostnames_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `songs_id`) ,
  CONSTRAINT `fk_requests_songs1`
    FOREIGN KEY (`songs_id` )
    REFERENCES `radio_main`.`songs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_requests_listeners1`
    FOREIGN KEY (`listeners_id` )
    REFERENCES `radio_main`.`listeners` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_requests_hostnames1`
    FOREIGN KEY (`hostnames_id` )
    REFERENCES `radio_main`.`hostnames` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE INDEX `fk_requests_songs1` ON `radio_main`.`requests` (`songs_id` ASC) ;

CREATE INDEX `fk_requests_listeners1` ON `radio_main`.`requests` (`listeners_id` ASC) ;

CREATE INDEX `fk_requests_hostnames1` ON `radio_main`.`requests` (`hostnames_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`played`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`played` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`played` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ,
  `songs_id` INT(12) NOT NULL ,
  `djs_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `songs_id`) ,
  CONSTRAINT `fk_lastplayed_songs1`
    FOREIGN KEY (`songs_id` )
    REFERENCES `radio_main`.`songs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_lastplayed_djs1`
    FOREIGN KEY (`djs_id` )
    REFERENCES `radio_main`.`djs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE INDEX `fk_lastplayed_songs1` ON `radio_main`.`played` (`songs_id` ASC) ;

CREATE INDEX `fk_lastplayed_djs1` ON `radio_main`.`played` (`djs_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`collection_editors`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`collection_editors` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`collection_editors` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `users_id` INT(12) NOT NULL ,
  `action` VARCHAR(45) NULL DEFAULT 'ACCEPTED' ,
  `time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ,
  `collection_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `collection_id`, `users_id`) ,
  CONSTRAINT `fk_collection_editors_auth_user1`
    FOREIGN KEY (`users_id` )
    REFERENCES `radio_main`.`auth_user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_collection_editors_collection1`
    FOREIGN KEY (`collection_id` )
    REFERENCES `radio_main`.`collection` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;

CREATE INDEX `fk_collection_editors_auth_user1` ON `radio_main`.`collection_editors` (`users_id` ASC) ;

CREATE INDEX `fk_collection_editors_collection1` ON `radio_main`.`collection_editors` (`collection_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`faves`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`faves` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`faves` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ,
  `songs_id` INT(12) NOT NULL ,
  `nicknames_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `songs_id`, `nicknames_id`) ,
  CONSTRAINT `fk_faves_songs1`
    FOREIGN KEY (`songs_id` )
    REFERENCES `radio_main`.`songs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_faves_nicknames1`
    FOREIGN KEY (`nicknames_id` )
    REFERENCES `radio_main`.`nicknames` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_faves_songs1` ON `radio_main`.`faves` (`songs_id` ASC) ;

CREATE INDEX `fk_faves_nicknames1` ON `radio_main`.`faves` (`nicknames_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`queue`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`queue` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`queue` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `type` TINYINT(1) NULL DEFAULT 0 ,
  `songs_id` INT(12) NOT NULL ,
  `time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  PRIMARY KEY (`id`, `songs_id`) ,
  CONSTRAINT `fk_queue_songs1`
    FOREIGN KEY (`songs_id` )
    REFERENCES `radio_main`.`songs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_queue_songs1` ON `radio_main`.`queue` (`songs_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`current_listeners`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`current_listeners` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`current_listeners` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `listeners_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `listeners_id`) ,
  CONSTRAINT `fk_current_listeners_listeners1`
    FOREIGN KEY (`listeners_id` )
    REFERENCES `radio_main`.`listeners` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_current_listeners_listeners1` ON `radio_main`.`current_listeners` (`listeners_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`streamstatus`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`streamstatus` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`streamstatus` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `listener_count` INT(12) NULL DEFAULT 0 ,
  `start_time` BIGINT UNSIGNED NULL DEFAULT 0 ,
  `end_time` BIGINT UNSIGNED NULL DEFAULT 0 ,
  `songs_id` INT(12) NOT NULL ,
  `djs_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `songs_id`) ,
  CONSTRAINT `fk_streamstatus_songs1`
    FOREIGN KEY (`songs_id` )
    REFERENCES `radio_main`.`songs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_streamstatus_djs1`
    FOREIGN KEY (`djs_id` )
    REFERENCES `radio_main`.`djs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_streamstatus_songs1` ON `radio_main`.`streamstatus` (`songs_id` ASC) ;

CREATE INDEX `fk_streamstatus_djs1` ON `radio_main`.`streamstatus` (`djs_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`uploads`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`uploads` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`uploads` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `listeners_id` INT(12) NOT NULL ,
  `time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ,
  `collection_id` INT(12) NOT NULL ,
  PRIMARY KEY (`id`, `listeners_id`, `collection_id`) ,
  CONSTRAINT `fk_uploads_listeners1`
    FOREIGN KEY (`listeners_id` )
    REFERENCES `radio_main`.`listeners` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_uploads_collection1`
    FOREIGN KEY (`collection_id` )
    REFERENCES `radio_main`.`collection` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_uploads_listeners1` ON `radio_main`.`uploads` (`listeners_id` ASC) ;

CREATE INDEX `fk_uploads_collection1` ON `radio_main`.`uploads` (`collection_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`album`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`album` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`album` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(200) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `radio_main`.`album` (`name` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`track_has_album`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`track_has_album` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`track_has_album` (
  `track_id` INT(12) NOT NULL ,
  `album_id` INT(12) NOT NULL ,
  PRIMARY KEY (`track_id`, `album_id`) ,
  CONSTRAINT `fk_track_has_album_track1`
    FOREIGN KEY (`track_id` )
    REFERENCES `radio_main`.`track` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_track_has_album_album1`
    FOREIGN KEY (`album_id` )
    REFERENCES `radio_main`.`album` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_track_has_album_album1` ON `radio_main`.`track_has_album` (`album_id` ASC) ;

CREATE INDEX `fk_track_has_album_track1` ON `radio_main`.`track_has_album` (`track_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`tags`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`tags` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`tags` (
  `id` INT(12) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(100) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `radio_main`.`tags` (`name` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`collection_has_tags`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`collection_has_tags` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`collection_has_tags` (
  `tags_id` INT(12) NOT NULL ,
  `collection_id` INT(12) NOT NULL ,
  PRIMARY KEY (`tags_id`, `collection_id`) ,
  CONSTRAINT `fk_collection_has_tags_tags1`
    FOREIGN KEY (`tags_id` )
    REFERENCES `radio_main`.`tags` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_collection_has_tags_collection1`
    FOREIGN KEY (`collection_id` )
    REFERENCES `radio_main`.`collection` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_collection_has_tags_tags1` ON `radio_main`.`collection_has_tags` (`tags_id` ASC) ;

CREATE INDEX `fk_collection_has_tags_collection1` ON `radio_main`.`collection_has_tags` (`collection_id` ASC) ;


-- -----------------------------------------------------
-- Table `radio_main`.`relays`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `radio_main`.`relays` ;

CREATE  TABLE IF NOT EXISTS `radio_main`.`relays` (
  `id` INT(12) NOT NULL ,
  `relay_name` VARCHAR(200) NOT NULL DEFAULT '' ,
  `relay_owner` VARCHAR(200) NOT NULL DEFAULT '' ,
  `base_name` VARCHAR(200) NOT NULL DEFAULT '' ,
  `port` INT(14) NOT NULL DEFAULT 1130 ,
  `mount` VARCHAR(200) NOT NULL DEFAULT '/main.mp3' ,
  `bitrate` INT(12) NOT NULL DEFAULT 192 ,
  `format` VARCHAR(15) NOT NULL DEFAULT 'mp3' ,
  `listeners` INT(12) NOT NULL DEFAULT 0 ,
  `listener_limit` INT(12) NULL DEFAULT NULL ,
  `active` TINYINT(1) NOT NULL DEFAULT False ,
  `admin_auth` VARCHAR(200) NOT NULL DEFAULT '' ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;

DROP TRIGGER IF EXISTS track_hash_insert;
DROP TRIGGER IF EXISTS track_hash_update;
DELIMITER //
CREATE TRIGGER track_hash_insert BEFORE INSERT ON track FOR EACH ROW BEGIN
    SET NEW.hash = SHA1(LOWER(NEW.metadata));
    END//
CREATE TRIGGER track_hash_update BEFORE UPDATE ON track FOR EACH ROW BEGIN
    SET NEW.hash = SHA1(LOWER(NEW.metadata));
    END//
DELIMITER ;

DROP TRIGGER IF EXISTS listeners_last_seen_update;
DELIMITER //
CREATE TRIGGER listeners_last_seen_update BEFORE UPDATE ON listeners FOR EACH ROW BEGIN
    SET NEW.last_seen = GREATEST(NEW.last_seen, OLD.last_seen);
    END//
DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
