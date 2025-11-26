-- Supabase schema for Save-Share
create table if not exists public.games (
  id uuid primary key default gen_random_uuid(),
  system text not null,
  rom_hash text not null,
  rom_name text not null,
  created_at timestamp with time zone default now(),
  unique(system, rom_hash)
);

create table if not exists public.saves (
  id uuid primary key default gen_random_uuid(),
  game_id uuid references public.games(id) on delete cascade,
  save_type text not null check (save_type in ('sram', 'state')),
  core text,
  tags text[] default array[]::text[],
  description text,
  uploader_nickname text,
  storage_path text,
  downloads integer default 0,
  created_at timestamp with time zone default now()
);

create view if not exists public.saves_view as
select s.id,
       g.system,
       g.rom_hash,
       g.rom_name,
       s.save_type,
       s.core,
       s.tags,
       s.description,
       s.uploader_nickname,
       s.storage_path,
       s.downloads,
       s.created_at
from public.saves s
join public.games g on s.game_id = g.id;
