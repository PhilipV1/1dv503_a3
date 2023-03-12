create database book_store;

use book_store;

CREATE TABLE books (
isbn char(10) NOT NULL,
author VARCHAR(100) NOT NULL,
title VARCHAR(128) NOT NULL,
price FLOAT,
subject VARCHAR(30),
PRIMARY KEY (isbn)
);

CREATE TABLE members (
  fname VARCHAR(20) NOT NULL,
  lname VARCHAR(20) NOT NULL,
  address VARCHAR(50) NOT NULL,
  city VARCHAR(30) NOT NULL,
  state VARCHAR(20) NOT NULL,
  zip INT NOT NULL,
  phone VARCHAR(12),
  email VARCHAR(40) UNIQUE,
  userid INT NOT NULL auto_increment,
  password VARCHAR(20),
  creditcardtype VARCHAR(10),
  creditcardnumber VARCHAR(16),
  PRIMARY KEY (userid)
  );

CREATE TABLE cart (
userid INT NOT NULL,
isbn CHAR(10) NOT NULL,
qty INT,
foreign key (userid) references members (userid),
foreign key (isbn) references books (isbn)
);
  
  CREATE TABLE orders (
  userid INT NOT NULL,
  ono INT NOT NULL auto_increment,
  recieved DATE,
  shipped DATE,
  shipAdress VARCHAR(50),
  shipCity VARCHAR(30),
  shipState VARCHAR(20),
  shipZip INT,
  foreign key (userid) references members (userid),
  PRIMARY KEY (ono)
  );
  
  CREATE TABLE odetails (
  ono INT NOT NULL,
  isbn CHAR(10) NOT NULL,
  qty INT,
  price FLOAT,
  foreign key (ono) references orders (ono),
  foreign key (isbn) references books (isbn)
  );