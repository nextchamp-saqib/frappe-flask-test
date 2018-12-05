-- DROP TABLE IF EXISTS products;
-- DROP TABLE IF EXISTS warehouses;
-- DROP TABLE IF EXISTS warehouse_details;
-- DROP TABLE IF EXISTS transfers;

-- CREATE TABLE products(
--   pname TEXT NOT NULL PRIMARY KEY,
--   pqty TEXT NOT NULL
-- );

-- CREATE TABLE warehouses(
--   wid TEXT PRIMARY KEY,
--   wname TEXT NOT NULL,
--   wloc TEXT NOT NULL
-- );

-- CREATE TABLE warehouse_details(
--   wdid INTEGER PRIMARY KEY,
--   wid TEXT,
--   pname TEXT,
--   pqty INTEGER NOT NULL DEFAULT 0,
--   FOREIGN KEY(wid) REFERENCES warehouses(wid),
--   FOREIGN KEY(pname) REFERENCES products(pname)
-- );

-- CREATE TABLE transfers(
--   tid INTEGER PRIMARY KEY,
--   tfrom INTEGER,
--   tto INTEGER,
--   pname TEXT NOT NULL,
--   tqty INTEGER NOT NULL,
--   timestmp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );