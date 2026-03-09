-- 1. Podstawowe rozszerzenia
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

-- 2. Konfiguracja Full Text Search dla języka polskiego
-- PostgreSQL automatycznie doda rozszerzenia .dict i .affix do nazw podanych poniżej
CREATE TEXT SEARCH DICTIONARY public.polish_hunspell (
    TEMPLATE = pg_catalog.ispell,
    dictfile = 'pl_pl', 
    afffile = 'pl_pl', 
    stopwords = 'polish' 
);

CREATE TEXT SEARCH CONFIGURATION public.polish (
    PARSER = pg_catalog."default" 
);

-- Mapowanie typów wyrazów na słownik Hunspell
ALTER TEXT SEARCH CONFIGURATION public.polish
    ADD MAPPING FOR asciiword, word, hword_part, hword_asciipart, asciihword, hword
    WITH public.polish_hunspell, simple;

ALTER TEXT SEARCH CONFIGURATION public.polish
    ADD MAPPING FOR numword, email, url, host, sfloat, version, hword_numpart, numhword, url_path, file, "float", "int", uint
    WITH simple;

-- 3. Struktura tabel
CREATE TABLE public.recipes (
    id SERIAL PRIMARY KEY,
    title text,
    raw_text text,
    cleaned_text text,
    structured jsonb,
    language text DEFAULT 'pl'::text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    search_vector tsvector,
    status text DEFAULT 'processing'::text
);

CREATE TABLE public.recipe_embeddings (
    recipe_id integer NOT NULL PRIMARY KEY REFERENCES public.recipes(id) ON DELETE CASCADE,
    embedding public.vector(768)
);

CREATE TABLE public.recipe_images (
    id SERIAL PRIMARY KEY,
    recipe_id integer REFERENCES public.recipes(id) ON DELETE CASCADE,
    file_path text NOT NULL,
    image_type text,
    created_at timestamp without time zone DEFAULT now()
);

-- Trigger do automatycznego generowania wektora ułatwiającego wyszukiwanie (Full Text Search)
CREATE FUNCTION public.recipes_search_trigger() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
     setweight(to_tsvector('public.polish', coalesce(NEW.title, '')), 'A') ||
     setweight(to_tsvector('public.polish', coalesce(NEW.cleaned_text, '')), 'C') ||
     setweight(to_tsvector('public.polish', coalesce(NEW.raw_text, '')), 'D');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
    ON public.recipes FOR EACH ROW EXECUTE FUNCTION public.recipes_search_trigger();

-- Indeks GIN dla wyszukiwania pełnotekstowego
CREATE INDEX idx_search ON public.recipes USING gin (search_vector);

-- 4. Uprawnienia
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO recipes_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO recipes_user;

SELECT pg_catalog.setval('public.recipes_id_seq', 20, true);
