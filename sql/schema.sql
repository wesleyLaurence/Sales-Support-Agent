-- DriftDesk Support schema (MySQL)
CREATE DATABASE IF NOT EXISTS driftdesk_support;
USE driftdesk_support;

CREATE TABLE IF NOT EXISTS customers (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
  order_id VARCHAR(32) PRIMARY KEY,
  customer_id INT NOT NULL,
  status VARCHAR(32) NOT NULL,
  order_total DECIMAL(10,2) NOT NULL,
  ordered_at DATE NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS support_tickets (
  ticket_id VARCHAR(32) PRIMARY KEY,
  customer_id INT NOT NULL,
  order_id VARCHAR(32),
  subject VARCHAR(255) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'open',
  priority VARCHAR(16) NOT NULL DEFAULT 'normal',
  channel VARCHAR(32) NOT NULL DEFAULT 'chat',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  closed_at TIMESTAMP NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ticket_updates (
  update_id INT AUTO_INCREMENT PRIMARY KEY,
  ticket_id VARCHAR(32) NOT NULL,
  update_type VARCHAR(32) NOT NULL,
  note TEXT NOT NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ticket_tags (
  ticket_id VARCHAR(32) NOT NULL,
  tag VARCHAR(64) NOT NULL,
  PRIMARY KEY (ticket_id, tag),
  FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS etl_ingest_log (
  ingest_id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(128) NOT NULL,
  records_loaded INT NOT NULL DEFAULT 0,
  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'running'
) ENGINE=InnoDB;

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_tickets_customer ON support_tickets(customer_id);
CREATE INDEX idx_tickets_status ON support_tickets(status);
CREATE INDEX idx_updates_ticket ON ticket_updates(ticket_id);
