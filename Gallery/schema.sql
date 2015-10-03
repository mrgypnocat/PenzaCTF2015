

SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+0:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL REFERENCES authors(id),
    title VARCHAR(512) NOT NULL,
    text MEDIUMTEXT NOT NULL,
    hidden_text MEDIUMTEXT NOT NULL,
    published DATETIME NOT NULL,
    updated TIMESTAMP NOT NULL,
    filepath MEDIUMTEXT,
    KEY (published)
);

DROP TABLE IF EXISTS authors;
CREATE TABLE authors (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL REFERENCES authors(id),
    entry_id INT NOT NULL REFERENCES entries(id),
    text MEDIUMTEXT NOT NULL,
    published DATETIME NOT NULL,
    KEY (published)
);

INSERT INTO `gallery`.`authors` (`id`, `name`, `hashed_password`) VALUES ('0', 'fucker', 'fucker');
