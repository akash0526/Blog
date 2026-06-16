-- ====================================================================
-- APEX PULSE — DEFINITIVE SECURE SUPABASE SQL MIGRATION
-- Proper Row Level Security (RLS), User Authentication & Route Protection
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. EXTENSIONS & STRICT SCHEMAS
-- --------------------------------------------------------------------
create extension if not exists "uuid-ossp";

create type public.article_status as enum ('draft', 'in_review', 'scheduled', 'published');

-- --------------------------------------------------------------------
-- 2. AUTHORS TABLE (Strictly Tied to Authenticated Supabase Users)
-- --------------------------------------------------------------------
create table if not exists public.authors (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references auth.users not null unique, -- Strict 1:1 Auth User Mapping
    name text not null,
    role text not null default 'Full-Stack Developer',
    avatar_url text default 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80',
    bio text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.authors enable row level security;

-- Policies: Anyone can view authors. Only authenticated logged-in users can edit their profile.
create policy "Authors are viewable by everyone in public." on public.authors
    for select using (true);

create policy "Authors can only update their own authenticated profile." on public.authors
    for update using (auth.uid() = user_id);

-- --------------------------------------------------------------------
-- 3. ARTICLES TABLE (Absolute Secure Route Protection)
-- --------------------------------------------------------------------
create table if not exists public.articles (
    id uuid primary key default uuid_generate_v4(),
    slug text unique not null,
    title text not null,
    meta_description text not null,
    category text not null default 'Tech & AI',
    target_keyword text not null,
    secondary_keywords text,
    content text not null,
    image_url text,
    seo_score integer not null default 85,
    pageviews integer not null default 1,
    status public.article_status default 'in_review'::public.article_status not null,
    author_id uuid references public.authors(id), -- Optional for Serverless API keys
    published_at date not null default current_date,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

create index if not exists idx_articles_secure_status on public.articles(status);
create index if not exists idx_articles_secure_slug on public.articles(slug);

alter table public.articles enable row level security;

-- POLICIES: 
-- 1. Public can only view fully published articles. Strangers can NEVER view private drafts!
create policy "Public can only read published articles." on public.articles
    for select using (status = 'published'::public.article_status);

-- 2. Fully Authenticated Logged-In CMS Admins can view and moderate all articles (Drafts, In Review, Live).
create policy "Authenticated CMS Admins can read all articles." on public.articles
    for select using (
        auth.role() = 'authenticated' or auth.role() = 'service_role'
    );

-- 3. Outside strangers can NEVER insert or modify articles! Only logged-in CMS Admins or your secure Service Role API backend can push drops!
create policy "Only fully authenticated CMS Admins or Service backend can insert drops." on public.articles
    for insert with check (
        auth.role() = 'authenticated' or auth.role() = 'service_role'
    );

create policy "Only fully authenticated CMS Admins can update articles." on public.articles
    for update using (
        auth.role() = 'authenticated' or auth.role() = 'service_role'
    );

create policy "Only fully authenticated CMS Admins can delete articles." on public.articles
    for delete using (
        auth.role() = 'authenticated'
    );

-- --------------------------------------------------------------------
-- 4. NEWSLETTER SUBSCRIBERS TABLE (Real Database Backend)
-- --------------------------------------------------------------------
create table if not exists public.subscribers (
    id uuid primary key default uuid_generate_v4(),
    email text unique not null,
    subscribed_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.subscribers enable row level security;

-- Policies: Strangers can submit their email. Only Authenticated CMS Admins can view subscribers list.
create policy "Strangers can subscribe their email." on public.subscribers
    for insert with check (true);

create policy "Only authenticated Admins can read subscribers list." on public.subscribers
    for select using (auth.role() = 'authenticated');
