-- Allow public read for games and saves_view
alter table public.games enable row level security;
alter table public.saves enable row level security;

create policy "Public read games" on public.games
for select using (true);

create policy "Public read saves" on public.saves
for select using (true);

create policy "Public insert games" on public.games
for insert with check (true);

create policy "Public insert saves" on public.saves
for insert with check (true);

-- Optional: allow updating download counter
create policy "Update downloads" on public.saves
for update using (true) with check (true);
