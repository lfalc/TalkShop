-- Seed/example user profiles (also safe to re-run via upsert).

insert into public.user_profiles (
  user_id,
  gender,
  products,
  metadata,
  profile_created_at,
  profile_last_updated,
  total_selections,
  total_rejections,
  profile_confidence
)
values
(
  'usr_3f9d7e2c',
  'female',
  '{
    "shoe": {
      "size": "8.5",
      "attributes": {
        "brands": { "preferred": ["Gucci", "Balenciaga", "Golden Goose", "Common Projects"], "avoided": ["budget-brands"] },
        "types": { "preferred": ["sneaker", "loafer", "boot"], "avoided": ["athletic"] },
        "colors": { "preferred": ["white", "black", "metallic-gold", "blush-pink"], "avoided": ["neon"] },
        "materials": { "preferred": ["leather", "suede"], "avoided": ["synthetic", "canvas"] },
        "price_range": { "min": 300, "max": 1200, "currency": "USD" },
        "style_tags": ["luxury", "designer", "minimalist", "statement"],
        "use_cases": ["formal", "casual-chic", "events"]
      },
      "interaction_history": { "selections_count": 22, "rejections_count": 15, "last_interaction": "2026-02-06T10:05:00Z" }
    },
    "tshirt": {
      "size": "S",
      "attributes": {
        "materials": { "preferred": ["organic-cotton", "modal", "linen"], "avoided": ["polyester", "blend"] },
        "fit_types": { "preferred": ["slim-fit", "regular-fit"], "avoided": ["oversized"] },
        "sleeve_types": { "preferred": ["short-sleeve"] },
        "neck_types": { "preferred": ["crew-neck", "v-neck"] },
        "colors": { "preferred": ["white", "black", "cream", "soft-pastels"], "avoided": ["bright-colors", "neon"] },
        "patterns": { "preferred": ["solid", "subtle-logo"], "avoided": ["graphic", "bold-patterns"] },
        "brands": { "preferred": ["Theory", "Vince", "James Perse", "Rag & Bone"], "avoided": ["fast-fashion"] },
        "price_range": { "min": 80, "max": 250, "currency": "USD" },
        "style_tags": ["luxury", "minimalist", "elevated-basics", "timeless"]
      },
      "interaction_history": { "selections_count": 17, "rejections_count": 9, "last_interaction": "2026-02-06T09:50:00Z" }
    }
  }'::jsonb,
  '{
    "created_at": "2026-01-08T09:45:00Z",
    "last_updated": "2026-02-06T10:05:00Z",
    "total_selections": 39,
    "total_rejections": 24,
    "profile_confidence": 0.88
  }'::jsonb,
  '2026-01-08T09:45:00Z'::timestamptz,
  '2026-02-06T10:05:00Z'::timestamptz,
  39,
  24,
  0.88
),
(
  'usr_7b2a8f3e',
  'male',
  '{
    "shoe": {
      "size": "11",
      "attributes": {
        "brands": { "preferred": ["Jordan", "Yeezy", "Off-White", "Supreme"], "avoided": ["generic-brands"] },
        "types": { "preferred": ["sneaker"], "avoided": ["dress-shoe", "loafer", "sandal"] },
        "colors": { "preferred": ["black", "white", "red", "earth-tones"], "avoided": ["pastel-colors"] },
        "materials": { "preferred": ["leather", "suede", "canvas"], "avoided": [] },
        "price_range": { "min": 150, "max": 500, "currency": "USD" },
        "style_tags": ["streetwear", "luxury", "retro", "limited-edition"],
        "use_cases": ["casual", "collectors"]
      },
      "interaction_history": { "selections_count": 18, "rejections_count": 22, "last_interaction": "2026-02-06T11:00:00Z" }
    },
    "tshirt": {
      "size": "L",
      "attributes": {
        "materials": { "preferred": ["cotton", "blend"], "avoided": [] },
        "fit_types": { "preferred": ["oversized", "relaxed-fit"], "avoided": ["slim-fit"] },
        "sleeve_types": { "preferred": ["short-sleeve"] },
        "neck_types": { "preferred": ["crew-neck"] },
        "colors": { "preferred": ["black", "white", "earth-tones", "vintage-wash"], "avoided": ["bright-pink", "neon"] },
        "patterns": { "preferred": ["graphic", "logo", "abstract"], "avoided": ["plain"] },
        "brands": { "preferred": ["Supreme", "Stussy", "Palace", "Bape", "Off-White"], "avoided": ["fast-fashion-brands"] },
        "price_range": { "min": 50, "max": 300, "currency": "USD" },
        "style_tags": ["streetwear", "vintage", "bold", "limited-edition"]
      },
      "interaction_history": { "selections_count": 15, "rejections_count": 18, "last_interaction": "2026-02-06T10:30:00Z" }
    }
  }'::jsonb,
  '{
    "created_at": "2026-01-10T15:00:00Z",
    "last_updated": "2026-02-06T11:00:00Z",
    "total_selections": 33,
    "total_rejections": 40,
    "profile_confidence": 0.72
  }'::jsonb,
  '2026-01-10T15:00:00Z'::timestamptz,
  '2026-02-06T11:00:00Z'::timestamptz,
  33,
  40,
  0.72
),
(
  'usr_8a3f2b1c',
  'male',
  '{
    "shoe": {
      "size": "10",
      "attributes": {
        "brands": { "preferred": ["Nike", "Adidas", "New Balance"], "avoided": ["Skechers"] },
        "types": { "preferred": ["sneaker", "athletic"], "avoided": ["dress-shoe", "loafer"] },
        "colors": { "preferred": ["black", "white", "navy"], "avoided": ["neon-green", "pink"] },
        "materials": { "preferred": ["mesh", "knit"], "avoided": ["leather"] },
        "price_range": { "min": 80, "max": 200, "currency": "USD" },
        "style_tags": ["sporty", "minimalist", "modern"],
        "use_cases": ["gym", "casual", "running"]
      },
      "interaction_history": { "selections_count": 12, "rejections_count": 8, "last_interaction": "2026-02-05T14:32:00Z" }
    },
    "tshirt": {
      "size": "M",
      "attributes": {
        "materials": { "preferred": ["cotton", "blend"], "avoided": ["polyester"] },
        "fit_types": { "preferred": ["athletic-fit", "slim-fit"], "avoided": ["oversized"] },
        "sleeve_types": { "preferred": ["short-sleeve"] },
        "neck_types": { "preferred": ["crew-neck", "v-neck"] },
        "colors": { "preferred": ["black", "gray", "navy", "white"], "avoided": ["yellow", "bright-orange"] },
        "patterns": { "preferred": ["solid", "subtle-logo"], "avoided": ["graphic", "abstract"] },
        "brands": { "preferred": ["Nike", "Under Armour", "Lululemon"], "avoided": [] },
        "price_range": { "min": 25, "max": 60, "currency": "USD" },
        "style_tags": ["athleisure", "minimalist", "casual"]
      },
      "interaction_history": { "selections_count": 8, "rejections_count": 5, "last_interaction": "2026-02-04T10:15:00Z" }
    }
  }'::jsonb,
  '{
    "created_at": "2026-01-15T08:00:00Z",
    "last_updated": "2026-02-05T14:32:00Z",
    "total_selections": 20,
    "total_rejections": 13,
    "profile_confidence": 0.78
  }'::jsonb,
  '2026-01-15T08:00:00Z'::timestamptz,
  '2026-02-05T14:32:00Z'::timestamptz,
  20,
  13,
  0.78
),
(
  'usr_9c4d5e2f',
  'female',
  '{
    "shoe": {
      "size": "8",
      "attributes": {
        "brands": { "preferred": ["Allbirds", "Veja", "Cole Haan"], "avoided": ["Crocs"] },
        "types": { "preferred": ["loafer", "casual", "sneaker"], "avoided": ["boot", "sandal"] },
        "colors": { "preferred": ["beige", "white", "light-gray", "tan"], "avoided": ["red", "bright-blue"] },
        "materials": { "preferred": ["leather", "canvas"], "avoided": ["synthetic"] },
        "price_range": { "min": 100, "max": 250, "currency": "USD" },
        "style_tags": ["minimalist", "sustainable", "professional"],
        "use_cases": ["work", "casual"]
      },
      "interaction_history": { "selections_count": 6, "rejections_count": 4, "last_interaction": "2026-02-06T09:20:00Z" }
    },
    "tshirt": {
      "size": "S",
      "attributes": {
        "materials": { "preferred": ["organic-cotton", "modal", "linen"], "avoided": ["polyester"] },
        "fit_types": { "preferred": ["regular-fit", "relaxed-fit"], "avoided": ["slim-fit"] },
        "sleeve_types": { "preferred": ["short-sleeve", "3-quarter"] },
        "neck_types": { "preferred": ["crew-neck", "v-neck"] },
        "colors": { "preferred": ["white", "beige", "olive", "black", "soft-pink"], "avoided": ["neon-colors", "bright-red"] },
        "patterns": { "preferred": ["solid", "plain"], "avoided": ["graphic", "logo"] },
        "brands": { "preferred": ["Everlane", "Patagonia", "Uniqlo"], "avoided": [] },
        "price_range": { "min": 30, "max": 80, "currency": "USD" },
        "style_tags": ["minimalist", "sustainable", "casual", "professional"]
      },
      "interaction_history": { "selections_count": 10, "rejections_count": 3, "last_interaction": "2026-02-05T16:45:00Z" }
    }
  }'::jsonb,
  '{
    "created_at": "2026-01-20T12:30:00Z",
    "last_updated": "2026-02-06T09:20:00Z",
    "total_selections": 16,
    "total_rejections": 7,
    "profile_confidence": 0.85
  }'::jsonb,
  '2026-01-20T12:30:00Z'::timestamptz,
  '2026-02-06T09:20:00Z'::timestamptz,
  16,
  7,
  0.85
)
on conflict (user_id) do update set
  gender = excluded.gender,
  products = excluded.products,
  metadata = excluded.metadata,
  profile_created_at = excluded.profile_created_at,
  profile_last_updated = excluded.profile_last_updated,
  total_selections = excluded.total_selections,
  total_rejections = excluded.total_rejections,
  profile_confidence = excluded.profile_confidence;

