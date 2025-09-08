-- Run these in MySQL before starting the app
CREATE DATABASE IF NOT EXISTS devi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE devi;

-- Student registrations
CREATE TABLE IF NOT EXISTS student_registrations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  gender ENUM('Male','Female','Other') DEFAULT NULL,
  sport VARCHAR(50) DEFAULT NULL,
  department VARCHAR(100) DEFAULT NULL,
  contact VARCHAR(20) DEFAULT NULL,
  email VARCHAR(120) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from student_registrations;


-- Players (for Addplayer / Performance pages)
CREATE TABLE IF NOT EXISTS players (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  team VARCHAR(100) DEFAULT NULL,
  position VARCHAR(50) DEFAULT NULL,
  matches INT DEFAULT 0,
  goals INT DEFAULT 0,
  assists INT DEFAULT 0,
  energy TINYINT DEFAULT 100,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contacts (for /contact form)
CREATE TABLE IF NOT EXISTS contacts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(120) NOT NULL,
  message TEXT,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from contacts;
-- Admin user (very simple demo; consider proper auth in production)
CREATE TABLE IF NOT EXISTS admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  -- store hashed password in real apps! this is plain text for demo
  password VARCHAR(255) NOT NULL
);

INSERT IGNORE INTO admins (username, password) VALUES ('admin', 'admin123');
