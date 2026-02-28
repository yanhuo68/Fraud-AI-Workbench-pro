-- Insert into Categories first
INSERT INTO Categories (CategoryName) VALUES ('Electronics'), ('Home Office');

-- Insert into Products matching the IDs used in your OrderDetails
INSERT INTO Products (ProductName, Price, CategoryID) VALUES 
('Premium Fraud Monitoring Tool', 120.00, 1),
('Secure Token Generator', 30.00, 1);