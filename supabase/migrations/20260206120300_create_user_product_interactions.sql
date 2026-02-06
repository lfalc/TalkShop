-- Create junction table for user-product interactions
-- Tracks user sentiment and interactions with specific products

create table if not exists public.user_product_interactions (
  interaction_id text primary key default 'int_' || substr(gen_random_uuid()::text, 1, 8),
  
  user_id text not null,
  product_id text not null,
  
  sentiment text not null check (sentiment in ('good', 'bad')),
  sentiment_notes text,
  
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  
  -- Foreign key constraints
  constraint fk_user_product_interactions_user_id 
    foreign key (user_id) references public.user_profiles (user_id) on delete cascade,
  constraint fk_user_product_interactions_product_id 
    foreign key (product_id) references public.products (product_id) on delete cascade,
  
  -- Ensure one interaction per user-product pair
  constraint unique_user_product unique (user_id, product_id)
);

-- Indexes for efficient querying
create index if not exists user_product_interactions_user_id_idx on public.user_product_interactions (user_id);
create index if not exists user_product_interactions_product_id_idx on public.user_product_interactions (product_id);
create index if not exists user_product_interactions_sentiment_idx on public.user_product_interactions (sentiment);
create index if not exists user_product_interactions_created_at_idx on public.user_product_interactions (created_at desc);

-- Add the updated_at trigger
drop trigger if exists set_user_product_interactions_updated_at on public.user_product_interactions;
create trigger set_user_product_interactions_updated_at
before update on public.user_product_interactions
for each row execute procedure public.set_updated_at();