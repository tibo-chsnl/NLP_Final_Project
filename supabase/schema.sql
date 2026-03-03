create table feedback (
  id uuid default gen_random_uuid() primary key,
  context text not null,
  question text not null,
  answer text not null,
  original_answer text,
  positive boolean not null,
  processed boolean not null default false,
  processed_at timestamp with time zone,
  created_at timestamp with time zone default now()
);

-- Migration for existing table (run this if the table already exists):
-- ALTER TABLE feedback ADD COLUMN IF NOT EXISTS processed boolean NOT NULL DEFAULT false;
-- ALTER TABLE feedback ADD COLUMN IF NOT EXISTS processed_at timestamp with time zone;
