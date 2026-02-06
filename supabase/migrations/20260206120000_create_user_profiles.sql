-- Create a simple user profile table for TalkShop.
-- Uses a TEXT primary key (e.g. "usr_3f9d7e2c") instead of UUID.

create table if not exists public.user_profiles (
  user_id text primary key,
  gender text,

  -- Flexible payloads (matches provided example JSON shape)
  products jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,

  -- Convenient typed fields extracted from metadata for querying
  profile_created_at timestamptz,
  profile_last_updated timestamptz,
  total_selections integer,
  total_rejections integer,
  profile_confidence numeric(4,3),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint user_profiles_profile_confidence_between_0_and_1
    check (profile_confidence is null or (profile_confidence >= 0 and profile_confidence <= 1))
);

create index if not exists user_profiles_gender_idx on public.user_profiles (gender);
create index if not exists user_profiles_profile_last_updated_idx on public.user_profiles (profile_last_updated desc);

-- Maintain updated_at automatically.
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_user_profiles_updated_at on public.user_profiles;
create trigger set_user_profiles_updated_at
before update on public.user_profiles
for each row execute procedure public.set_updated_at();

