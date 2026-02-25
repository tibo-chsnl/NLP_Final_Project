create table feedback (
  id uuid default gen_random_uuid() primary key,
  context text not null,
  question text not null,
  answer text not null,
  original_answer text,
  positive boolean not null,
  created_at timestamp with time zone default now()
);
