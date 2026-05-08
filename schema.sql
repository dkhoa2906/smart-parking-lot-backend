-- ============================================================
-- Parking Monitoring System - Database Schema
-- Group 7 | CMP6210 Cloud Computing
-- Target: AWS RDS MySQL (us-east-1)
-- ============================================================

-- Drop tables in reverse FK order to avoid constraint errors
DROP TABLE IF EXISTS slot_history;
DROP TABLE IF EXISTS parking_slots;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS parking_lots;

-- ============================================================
-- Table: parking_lots
-- Stores information about each parking lot
-- ============================================================
CREATE TABLE parking_lots (
    id          INT             NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100)    NOT NULL,
    location    VARCHAR(255)    NOT NULL,
    total_slots INT             NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_parking_lots PRIMARY KEY (id),
    CONSTRAINT chk_total_slots CHECK (total_slots >= 0)
);

-- ============================================================
-- Table: users
-- Stores admin accounts for managing parking lots (one per lot)
-- ============================================================
CREATE TABLE users (
    id              INT             NOT NULL AUTO_INCREMENT,
    lot_id          INT             NOT NULL UNIQUE,   -- one-to-one with parking_lots
    username        VARCHAR(50)     NOT NULL,
    password        VARCHAR(255)    NOT NULL,          -- bcrypt hashed
    recovery_email  VARCHAR(255)    NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_users             PRIMARY KEY (id),
    CONSTRAINT uq_users_username    UNIQUE (username),
    CONSTRAINT uq_users_lot         UNIQUE (lot_id),
    CONSTRAINT fk_users_lot         FOREIGN KEY (lot_id)
        REFERENCES parking_lots(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================================
-- Table: parking_slots
-- Stores each individual slot within a parking lot
-- ============================================================
CREATE TABLE parking_slots (
    id          INT                     NOT NULL AUTO_INCREMENT,
    lot_id      INT                     NOT NULL,
    slot_number VARCHAR(10)             NOT NULL,
    status      ENUM('free','occupied') NOT NULL DEFAULT 'free',
    updated_at  DATETIME                NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_parking_slots         PRIMARY KEY (id),
    CONSTRAINT uq_slot_per_lot          UNIQUE (lot_id, slot_number),  -- A1 unique within each lot
    CONSTRAINT fk_parking_slots_lot     FOREIGN KEY (lot_id)
        REFERENCES parking_lots(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Index: speed up queries filtering slots by lot
CREATE INDEX idx_parking_slots_lot_id ON parking_slots(lot_id);

-- Index: speed up queries filtering slots by status (e.g. count free slots)
CREATE INDEX idx_parking_slots_status ON parking_slots(status);

-- ============================================================
-- Table: slot_history
-- Stores every detection event recorded by the camera/YOLOv8
-- ============================================================
CREATE TABLE slot_history (
    id          INT                     NOT NULL AUTO_INCREMENT,
    slot_id     INT                     NOT NULL,
    status      ENUM('free','occupied') NOT NULL,
    detected_at DATETIME                NOT NULL DEFAULT CURRENT_TIMESTAMP,
    image_key   VARCHAR(255)            NOT NULL,  -- S3 object key of source image

    CONSTRAINT pk_slot_history          PRIMARY KEY (id),
    CONSTRAINT fk_slot_history_slot     FOREIGN KEY (slot_id)
        REFERENCES parking_slots(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Index: speed up queries fetching history for a specific slot
CREATE INDEX idx_slot_history_slot_id   ON slot_history(slot_id);

-- Index: speed up queries filtering history by time range
CREATE INDEX idx_slot_history_detected  ON slot_history(detected_at);

-- ============================================================
-- Seed Data (optional - for testing)
-- ============================================================
INSERT INTO parking_lots (name, location, total_slots)
VALUES ('Group7 Parking Lot A', 'University Campus, Building C', 10);

INSERT INTO users (lot_id, username, password, recovery_email)
VALUES (1, 'admin_group7', '$2b$12$placeholder_hash_replace_me', 'group7@university.ac.uk');

INSERT INTO parking_slots (lot_id, slot_number, status) VALUES
(1, 'A1', 'free'),
(1, 'A2', 'free'),
(1, 'A3', 'free'),
(1, 'A4', 'free'),
(1, 'A5', 'free'),
(1, 'B1', 'free'),
(1, 'B2', 'free'),
(1, 'B3', 'free'),
(1, 'B4', 'free'),
(1, 'B5', 'free');
