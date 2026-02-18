-- Fix sessoes_local_check constraint to allow NULL and standard values
-- Run this with: psql -U postgres -d futebol_analytics -f fix_constraint.sql

\echo 'Fixing sessoes_local_check constraint...'

-- Drop existing constraint if it exists
ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_local_check;

-- Add new constraint that allows NULL or specific values
ALTER TABLE sessoes ADD CONSTRAINT sessoes_local_check 
CHECK (local IS NULL OR local IN ('Casa', 'Fora', 'Neutro'));

\echo 'Constraint fixed successfully!'

-- Verify the constraint
\echo 'Current constraint definition:'
SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
FROM pg_constraint 
WHERE conrelid = 'sessoes'::regclass AND conname = 'sessoes_local_check';
