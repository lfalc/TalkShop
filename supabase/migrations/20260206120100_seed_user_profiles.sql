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
  'usr_5n6k1e4f',
  'male',
  '{
    "shoe": {
      "size": "10.5",
      "attributes": {
        "brands": { "preferred": ["Nike"], "avoided": ["Adidas", "Puma", "other-brands"] },
        "types": { "preferred": ["sneaker", "athletic"], "avoided": ["dress-shoe", "loafer", "sandal", "boot"] },
        "colors": { "preferred": ["black", "white", "grey", "navy"], "avoided": ["bright-colors", "neon", "pink"] },
        "materials": { "preferred": ["leather", "knit", "mesh"], "avoided": ["canvas", "suede"] },
        "price_range": { "min": 100, "max": 300, "currency": "USD" },
        "style_tags": ["sleek", "modern", "athletic", "minimalist", "performance"],
        "use_cases": ["casual", "gym", "running", "everyday"],
        "profile_notes": ["prefers low-profile designs", "values sleek silhouettes", "Nike-only brand loyalty"]
      },
      "interaction_history": { "selections_count": 28, "rejections_count": 12, "last_interaction": "2026-02-07T08:30:00Z" }
    },
    "tshirt": {
      "size": "M",
      "attributes": {
        "materials": { "preferred": ["cotton", "blend", "performance-fabric"], "avoided": ["polyester-only"] },
        "fit_types": { "preferred": ["athletic-fit", "slim-fit"], "avoided": ["oversized", "loose-fit"] },
        "sleeve_types": { "preferred": ["short-sleeve"] },
        "neck_types": { "preferred": ["crew-neck"] },
        "colors": { "preferred": ["black", "white", "grey", "navy"], "avoided": ["bright-colors", "neon"] },
        "patterns": { "preferred": ["solid", "subtle-logo"], "avoided": ["graphic", "bold-patterns"] },
        "brands": { "preferred": ["Nike"], "avoided": ["other-brands"] },
        "price_range": { "min": 25, "max": 80, "currency": "USD" },
        "style_tags": ["athletic", "sleek", "minimalist", "performance"]
      },
      "interaction_history": { "selections_count": 19, "rejections_count": 7, "last_interaction": "2026-02-06T19:15:00Z" }
    }
  }'::jsonb,
  '{
    "created_at": "2026-01-25T11:20:00Z",
    "last_updated": "2026-02-07T08:30:00Z",
    "total_selections": 47,
    "total_rejections": 19,
    "profile_confidence": 0.91,
    "brand_loyalty": { "Nike": 0.95 }
  }'::jsonb,
  '2026-01-25T11:20:00Z'::timestamptz,
  '2026-02-07T08:30:00Z'::timestamptz,
  47,
  19,
  0.91
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

