CREATE DATABASE IF NOT EXISTS eurostar;
USE eurostar;
CREATE TABLE IF NOT EXISTS assistance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    genre VARCHAR(20) NOT NULL,
    age INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    handicap VARCHAR(255) NOT NULL,
    autre_handicap TEXT,
    ticket_number VARCHAR(6) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('nouvelle', 'en_cours', 'terminee') DEFAULT 'nouvelle',
    
    INDEX idx_ticket_number (ticket_number),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
);

INSERT IGNORE INTO assistance (nom, prenom, genre, age, email, handicap, autre_handicap, ticket_number) VALUES
('MARTIN', 'Sophie', 'Femme', 45, 'sophie.martin@example.com', 'Mobilité réduite', 'Fauteuil roulant électrique', '538826'),
('DUBOIS', 'Jean', 'Homme', 67, 'jean.dubois@example.com', 'Déficience visuelle', 'Accompagnement avec chien guide', '307899'),
('BERNARD', 'Marie', 'Femme', 34, 'marie.bernard@example.com', 'Autre', 'Voyage avec bébé, besoin d\'aide pour les bagages', '762907');