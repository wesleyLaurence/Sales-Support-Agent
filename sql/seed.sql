USE driftdesk_support;

INSERT INTO customers (email, full_name) VALUES
  ('alex@acme.co', 'Alex Rivera'),
  ('jamie@northwind.io', 'Jamie Patel'),
  ('taylor@oak.com', 'Taylor Kim'),
  ('sam@sunset.org', 'Sam Brooks'),
  ('casey@atlas.net', 'Casey Morgan')
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

INSERT INTO orders (order_id, customer_id, status, order_total, ordered_at) VALUES
  ('ORD-2001', 1, 'shipped', 699.00, '2024-12-10'),
  ('ORD-2002', 2, 'processing', 318.00, '2024-12-18'),
  ('ORD-2003', 3, 'delivered', 129.00, '2024-12-02'),
  ('ORD-2004', 4, 'delayed', 958.00, '2024-12-20')
ON DUPLICATE KEY UPDATE status = VALUES(status), order_total = VALUES(order_total);

INSERT INTO support_tickets (ticket_id, customer_id, order_id, subject, status, priority, channel, created_at) VALUES
  ('TCK-AX91', 1, 'ORD-2001', 'Desk control panel not responding', 'open', 'high', 'email', '2024-12-21 09:10:00'),
  ('TCK-BQ22', 2, 'ORD-2002', 'Shipping address change request', 'pending', 'normal', 'chat', '2024-12-22 14:30:00'),
  ('TCK-CM08', 4, 'ORD-2004', 'Delivery delayed beyond ETA', 'open', 'high', 'phone', '2024-12-23 11:05:00')
ON DUPLICATE KEY UPDATE status = VALUES(status), priority = VALUES(priority);

INSERT INTO ticket_updates (ticket_id, update_type, note, updated_at) VALUES
  ('TCK-AX91', 'customer', 'Panel is stuck on error code E3.', '2024-12-21 09:12:00'),
  ('TCK-AX91', 'agent', 'Requested a photo of the control panel.', '2024-12-21 09:20:00'),
  ('TCK-BQ22', 'customer', 'Need delivery moved to next week.', '2024-12-22 14:32:00'),
  ('TCK-CM08', 'agent', 'Carrier escalation opened.', '2024-12-23 11:10:00');

INSERT INTO ticket_tags (ticket_id, tag) VALUES
  ('TCK-AX91', 'hardware'),
  ('TCK-AX91', 'warranty'),
  ('TCK-BQ22', 'shipping'),
  ('TCK-CM08', 'shipping'),
  ('TCK-CM08', 'delay')
ON DUPLICATE KEY UPDATE tag = VALUES(tag);
