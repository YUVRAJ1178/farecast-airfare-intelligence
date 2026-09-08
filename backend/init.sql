-- Airfare Intelligence Platform — PostgreSQL Init Script
-- Run once on fresh database to ensure extensions are available.

CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- For text search
CREATE EXTENSION IF NOT EXISTS btree_gin; -- For composite indexes

-- Tables are created by SQLAlchemy on startup (Base.metadata.create_all)
-- This file only sets up extensions and any PostgreSQL-specific config.

-- Set timezone
SET timezone = 'UTC';
