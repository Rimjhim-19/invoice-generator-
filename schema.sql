CREATE TABLE IF NOT EXISTS clients (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    phone       TEXT,
    address     TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoices (
    id              SERIAL PRIMARY KEY,
    client_id       INTEGER NOT NULL REFERENCES clients(id),
    invoice_number  TEXT NOT NULL UNIQUE,
    issue_date      DATE NOT NULL,
    due_date        DATE NOT NULL,
    status          TEXT DEFAULT 'draft',
    tax_percent     NUMERIC(5,2) DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS line_items (
    id          SERIAL PRIMARY KEY,
    invoice_id  INTEGER NOT NULL REFERENCES invoices(id),
    description TEXT NOT NULL,
    quantity    NUMERIC(10,2) NOT NULL,
    rate        NUMERIC(10,2) NOT NULL
);