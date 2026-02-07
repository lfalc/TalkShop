-- Seed data for user_product_interactions table
-- Creating realistic interactions based on user preferences from user_profiles

insert into public.user_product_interactions (
  user_id,
  product_id,
  sentiment,
  sentiment_notes
) values

-- usr_5n6k1e4f (male, Nike-only brand loyalty with sleek shoe preferences)
(
  'usr_5n6k1e4f',
  'prd_nike_court_001',
  'good',
  'Perfect sleek design and exactly what I look for in Nike. Clean white leather with low profile - ideal for everyday wear.'
),
(
  'usr_5n6k1e4f',
  'prd_nike_blazer_001',
  'good',
  'Love the minimalist black leather and vintage vibes. Low-profile silhouette is exactly my style preference.'
),
(
  'usr_5n6k1e4f',
  'prd_nike_react_001',
  'good',
  'Amazing performance shoe with the sleek profile I prefer. Nike''s innovation at its best for serious running.'
),
(
  'usr_5n6k1e4f',
  'prd_nike_pegasus_001',
  'good',
  'Trusted Nike running shoe with the clean, sleek design I always choose. Perfect for both gym and casual wear.'
),
(
  'usr_5n6k1e4f',
  'prd_nike_killshot_001',
  'good',
  'Exactly the kind of minimalist Nike design I love. Simple, clean, and sleek - everything I want in a sneaker.'
),
(
  'usr_5n6k1e4f',
  'prd_nike_metcon_001',
  'good',
  'Great training shoe with the low-profile design I prefer. Nike quality and performance for intense workouts.'
),
(
  'usr_5n6k1e4f',
  'prd_adidas_athletic_001',
  'bad',
  'Wrong brand - I only shop Nike. Also doesn''t have the sleek profile I prefer in athletic shoes.'
),
(
  'usr_5n6k1e4f',
  'prd_jordan_sneaker_001',
  'bad',
  'Not Nike brand and too bulky for my taste. I prefer sleek, low-profile designs over chunky basketball shoes.'
),
(
  'usr_5n6k1e4f',
  'prd_yeezy_sneaker_001',
  'bad',
  'Wrong brand and the design is too chunky. I stick to Nike and prefer much sleeker silhouettes.'
),
(
  'usr_5n6k1e4f',
  'prd_newbalance_athletic_001',
  'bad',
  'Not Nike and the profile is too bulky for my preferences. I only trust Nike for athletic performance.'
),
(
  'usr_5n6k1e4f',
  'prd_veja_sneaker_001',
  'bad',
  'Wrong brand - I''m loyal to Nike only. Also doesn''t match the athletic aesthetic I prefer.'
),
(
  'usr_5n6k1e4f',
  'prd_allbirds_casual_001',
  'bad',
  'Not Nike and too casual/sustainable-focused for my athletic lifestyle. Need Nike performance features.'
)
on conflict (user_id, product_id) do update set
  sentiment = excluded.sentiment,
  sentiment_notes = excluded.sentiment_notes;