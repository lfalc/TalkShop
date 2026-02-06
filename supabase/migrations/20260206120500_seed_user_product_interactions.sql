-- Seed data for user_product_interactions table
-- Creating realistic interactions based on user preferences from user_profiles

insert into public.user_product_interactions (
  user_id,
  product_id,
  sentiment,
  sentiment_notes
) values
-- usr_3f9d7e2c (female, luxury preferences) - positive interactions with luxury brands
(
  'usr_3f9d7e2c',
  'prd_gucci_sneaker_001',
  'good',
  'Love the clean white leather and subtle luxury branding. Perfect for elevated casual outfits.'
),
(
  'usr_3f9d7e2c',
  'prd_balenciaga_boot_001',
  'good',
  'Beautiful silhouette and premium quality. Great for formal events and statement looks.'
),
(
  'usr_3f9d7e2c',
  'prd_commonprojects_sneaker_001',
  'good',
  'Exactly the minimalist aesthetic I love. Quality leather and timeless design.'
),
(
  'usr_3f9d7e2c',
  'prd_nike_athletic_001',
  'bad',
  'Too athletic-focused for my style. Prefer more sophisticated sneaker designs.'
),
(
  'usr_3f9d7e2c',
  'prd_allbirds_casual_001',
  'bad',
  'Material feels too casual and the price point doesn''t match my luxury preferences.'
),

-- usr_7b2a8f3e (male, streetwear preferences) - positive interactions with streetwear brands
(
  'usr_7b2a8f3e',
  'prd_jordan_sneaker_001',
  'good',
  'Classic colorway and iconic silhouette. Perfect for my streetwear collection.'
),
(
  'usr_7b2a8f3e',
  'prd_yeezy_sneaker_001',
  'good',
  'Love the earth tones and the limited-edition status. Great for casual fits.'
),
(
  'usr_7b2a8f3e',
  'prd_offwhite_sneaker_001',
  'good',
  'Amazing collaboration piece. The deconstructed design is exactly what I''m looking for.'
),
(
  'usr_7b2a8f3e',
  'prd_supreme_sneaker_001',
  'good',
  'Supreme collabs are always fire. Red colorway is bold and the quality is solid.'
),
(
  'usr_7b2a8f3e',
  'prd_allbirds_casual_001',
  'bad',
  'Too minimalist and sustainable-focused. Doesn''t fit my streetwear aesthetic.'
),
(
  'usr_7b2a8f3e',
  'prd_colehaan_loafer_001',
  'bad',
  'Way too formal and professional for my style. Prefer sneakers over dress shoes.'
),

-- usr_8a3f2b1c (male, athletic preferences) - positive interactions with athletic brands
(
  'usr_8a3f2b1c',
  'prd_nike_athletic_001',
  'good',
  'Great for gym workouts and running. Comfortable cushioning and modern design.'
),
(
  'usr_8a3f2b1c',
  'prd_adidas_athletic_001',
  'good',
  'Excellent performance shoe with boost technology. Perfect for serious training.'
),
(
  'usr_8a3f2b1c',
  'prd_newbalance_athletic_001',
  'good',
  'Superior comfort and quality construction. Made in USA is a nice bonus.'
),
(
  'usr_8a3f2b1c',
  'prd_gucci_sneaker_001',
  'bad',
  'Too luxury-focused and not functional enough for my athletic needs.'
),
(
  'usr_8a3f2b1c',
  'prd_goldengoose_sneaker_001',
  'bad',
  'Distressed look isn''t my style and too expensive for what you get functionally.'
),

-- usr_9c4d5e2f (female, sustainable preferences) - positive interactions with sustainable/professional brands
(
  'usr_9c4d5e2f',
  'prd_allbirds_casual_001',
  'good',
  'Perfect sustainable choice with comfortable fit. Great for work and casual days.'
),
(
  'usr_9c4d5e2f',
  'prd_veja_sneaker_001',
  'good',
  'Love the ethical production and clean aesthetic. Fits my values and style.'
),
(
  'usr_9c4d5e2f',
  'prd_colehaan_loafer_001',
  'good',
  'Professional yet comfortable for work. Quality leather and versatile design.'
),
(
  'usr_9c4d5e2f',
  'prd_supreme_sneaker_001',
  'bad',
  'Too flashy and streetwear-focused for my minimalist professional style.'
),
(
  'usr_9c4d5e2f',
  'prd_offwhite_sneaker_001',
  'bad',
  'Too bold and hype-focused. Doesn''t align with my sustainable and professional values.'
)
on conflict (user_id, product_id) do update set
  sentiment = excluded.sentiment,
  sentiment_notes = excluded.sentiment_notes;