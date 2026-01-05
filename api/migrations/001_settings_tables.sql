-- Migration: 001_settings_tables
-- Description: Create categories and settings tables for app configuration
-- Date: 2024-01-15

-- Categories table (per SPEC.md)
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    monthly_budget_limit DECIMAL(10,2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settings table (key-value store for app configuration)
CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    encrypted BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster settings lookups
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);

-- Seed default categories from SPEC.md
INSERT INTO categories (name, monthly_budget_limit) VALUES
    ('Groceries', NULL),
    ('Dining', NULL),
    ('Transportation', NULL),
    ('Utilities', NULL),
    ('Entertainment', NULL),
    ('Healthcare', NULL),
    ('Clothing', NULL),
    ('Home & Garden', NULL),
    ('Personal Care', NULL),
    ('Shopping', NULL),
    ('Other', NULL)
ON CONFLICT (name) DO NOTHING;

-- Seed default settings
INSERT INTO settings (key, value, encrypted) VALUES
    ('llm_provider', 'gemini', FALSE),
    ('llm_model', 'gemini-2.0-flash', FALSE),
    ('theme', 'system', FALSE)
ON CONFLICT (key) DO NOTHING;
