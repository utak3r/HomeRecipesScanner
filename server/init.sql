DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'supabase_admin') THEN
    CREATE ROLE supabase_admin;
  END IF;
END
$$;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgroonga;

CREATE OR REPLACE FUNCTION public.jsonb_to_text(data jsonb) RETURNS text
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
  result text;
BEGIN
  SELECT string_agg(v #>> '{}', ' ') INTO result
  FROM jsonb_path_query(data, '$.**') v
  WHERE jsonb_typeof(v) NOT IN ('object', 'array');
  RETURN coalesce(result, '');
END
$$;

-- --------------------------------

CREATE TABLE public.recipes (
    id SERIAL PRIMARY KEY,
    title text,
    full_text text,
    structured jsonb,
    language text DEFAULT 'pl',
    status text DEFAULT 'processing',
    source text DEFAULT 'ocr',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE TABLE public.tags (
    id SERIAL PRIMARY KEY,
    name text NOT NULL UNIQUE
);

CREATE TABLE public.recipe_tags (
    recipe_id integer REFERENCES public.recipes(id) ON DELETE CASCADE,
    tag_id integer REFERENCES public.tags(id) ON DELETE CASCADE,
    PRIMARY KEY (recipe_id, tag_id)
);

CREATE TABLE public.recipe_images (
    id SERIAL PRIMARY KEY,
    recipe_id integer REFERENCES public.recipes(id) ON DELETE CASCADE,
    file_path text NOT NULL,
    image_type text,
    page_number integer DEFAULT 1,
    created_at timestamptz DEFAULT now()
);

CREATE TABLE public.recipe_embeddings (
    recipe_id integer PRIMARY KEY REFERENCES public.recipes(id) ON DELETE CASCADE,
    embedding public.vector(768)
);

-- --------------------------------

CREATE OR REPLACE FUNCTION public.recipes_search_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.full_text := public.jsonb_to_text(NEW.structured);
  NEW.updated_at := now();
  RETURN NEW;
END
$$;

CREATE TRIGGER tsvectorupdate 
    BEFORE INSERT OR UPDATE ON public.recipes 
    FOR EACH ROW EXECUTE FUNCTION public.recipes_search_trigger();

-- --------------------------------

CREATE INDEX idx_recipes_pgroonga ON public.recipes USING pgroonga (title, full_text);
CREATE INDEX idx_recipe_embeddings_v_cosine ON public.recipe_embeddings 
USING hnsw (embedding vector_cosine_ops);
