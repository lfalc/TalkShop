-- Create products table for storing product memories and metadata
-- This table stores individual products that users have interacted with
-- and their detailed attributes for matching against user preferences

create table if not exists public.products (
  product_id text primary key,
  
  -- Basic product information
  name text not null,
  brand text,
  category text not null, -- e.g., 'shoe', 'tshirt', 'pants', etc.
  sub_category text, -- e.g., 'sneaker', 'boot', 'crew-neck', etc.
  
  -- Product details
  price numeric(10,2),
  currency text default 'USD',
  size text,
  color text,
  material text,
  
  -- Searchable attributes (matching user_profiles structure)
  attributes jsonb not null default '{}'::jsonb,
  
  -- URLs and media
  product_url text,
  image_path text, -- blob storage path for product image
  
  -- AI-generated summary (for LLM node output)
  product_summary text,
  
  -- Metadata for additional flexible data
  metadata jsonb not null default '{}'::jsonb,
  
  -- System timestamps
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  
  -- Constraints
  constraint products_price_positive check (price is null or price >= 0),
  constraint products_currency_length check (currency is null or length(currency) = 3)
);

-- Indexes for efficient searching and filtering
create index if not exists products_category_idx on public.products (category);
create index if not exists products_brand_idx on public.products (brand);
create index if not exists products_price_idx on public.products (price);

-- GIN index for JSONB attributes for fast attribute searches
create index if not exists products_attributes_gin_idx on public.products using gin (attributes);

-- Text search index for name and brand
create index if not exists products_text_search_idx on public.products using gin (
  to_tsvector('english', coalesce(name, '') || ' ' || coalesce(brand, ''))
);

-- Add the updated_at trigger
drop trigger if exists set_products_updated_at on public.products;
create trigger set_products_updated_at
before update on public.products
for each row execute procedure public.set_updated_at();