-- MedInsure Database Initialization
-- This script runs once when the container is first created.

-- Enable uuid extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE medinsure_db TO medinsure;

-- Log initialization
DO $$
BEGIN
  RAISE NOTICE 'MedInsure database initialized at %', NOW();
END $$;
