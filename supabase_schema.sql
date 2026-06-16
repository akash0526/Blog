-- ====================================================================
-- APEX PULSE — SUPABASE POSTGRESQL PRODUCTION SCHEMA
-- Professional Multi-Author, Hybrid Moderation Cloud Database
-- ====================================================================

-- Enable robust UUID generation
create extension if not exists "uuid-ossp";

-- --------------------------------------------------------------------
-- 1. AUTHORS TABLE (Managing E-E-A-T Verified Credentials)
-- --------------------------------------------------------------------
create table public.authors (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references auth.users not null, -- Ties to Supabase Auth
    name text not null,
    role text not null default 'Software Engineer',
    avatar_url text default 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80',
    bio text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable strict Row Level Security (RLS)
alter table public.authors enable row level security;

-- RLS Policies for Authors
create policy "Authors are viewable by everyone." on public.authors
    for select using (true);

create policy "Authors can update their own verified profile." on public.authors
    for update using (auth.uid() = user_id);

-- --------------------------------------------------------------------
-- 2. ARTICLES TABLE (Managing SEO Content & Human Review Workflow)
-- --------------------------------------------------------------------
create type article_status as enum ('draft', 'in_review', 'scheduled', 'published');

create table public.articles (
    id uuid primary key default uuid_generate_v4(),
    slug text unique not null,
    title text not null,
    meta_description text not null,
    category text not null default 'Tech & AI',
    target_keyword text not null,
    secondary_keywords text,
    content text not null, -- Stores markdown / rich prose
    image_url text,
    seo_score integer not null default 85,
    pageviews integer not null default 1,
    status article_status default 'in_review'::article_status not null, -- Default to HITL Review Queue
    author_id uuid references public.authors(id), -- Optional foreign key for serverless AI drops
    published_at date not null default current_date,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Performance Indexing for lightning-fast Edge CDN navigation
create index idx_articles_status on public.articles(status);
create index idx_articles_slug on public.articles(slug);
create index idx_articles_category on public.articles(category);

-- Enable Row Level Security (RLS)
alter table public.articles enable row level security;

-- RLS Policies for Articles
create policy "Published articles are completely public." on public.articles
    for select using (status = 'published'::article_status);

create policy "Authors can view and manage drafts or items in review." on public.articles
    for all using (
        auth.uid() in (
            select user_id from public.authors where authors.id = articles.author_id
        )
    );

-- --------------------------------------------------------------------
-- 3. AUTOMATED DATABASE TRIGGERS
-- --------------------------------------------------------------------
-- Auto-update updated_at timestamp whenever an article is modified
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger set_updated_at
    before update on public.articles
    for each row
    execute function public.handle_updated_at();

-- Notify External Deploy Webhook (e.g. Vercel) whenever a post becomes live
create or replace function public.notify_vercel_deploy()
returns trigger as $$
begin
    -- Performs a fast asynchronous Webhook ping to your Vercel Build token
    if new.status = 'published' and (old.status is distinct from 'published') then
        perform net.http_post(
            url := 'https://api.vercel.com/v1/integrations/deploy/YOUR_VERCEL_WEBHOOK_TOKEN',
            body := '{"state": "live_drop"}'::jsonb
        );
    end if;
    return new;
end;
$$ language plpgsql;
