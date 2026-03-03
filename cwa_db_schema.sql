--
-- PostgreSQL database dump
--

\restrict f45GTMSaaGlrm7Z9HCxAmpBRvIbQ8ue8WSttB6x2xsulxCfNx6QLbfIbeGi4s7D

-- Dumped from database version 17.6 (Postgres.app)
-- Dumped by pg_dump version 17.6 (Postgres.app)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: gllms_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.gllms_type_enum AS ENUM (
    'dummy',
    'ollama_local',
    'ollama_remote',
    'chatgpt',
    'gemini',
    'claude',
    'qwen'
);


--
-- Name: gvdbs_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.gvdbs_type_enum AS ENUM (
    'chroma',
    'qdrant',
    'pgvector'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: api_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_groups (
    group_id integer NOT NULL,
    deleted integer DEFAULT 0 NOT NULL,
    group_name character varying DEFAULT 'Undefined group'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: api_groups_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.api_groups_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: api_groups_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.api_groups_group_id_seq OWNED BY public.api_groups.group_id;


--
-- Name: api_processes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_processes (
    ap_id integer NOT NULL,
    ap_type character varying NOT NULL,
    ap_name character varying NOT NULL,
    ap_subname character varying DEFAULT ''::character varying NOT NULL,
    ap_status character varying DEFAULT ''::character varying NOT NULL,
    ap_json text DEFAULT '{}'::text NOT NULL,
    ap_updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: api_processes_ap_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.api_processes_ap_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: api_processes_ap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.api_processes_ap_id_seq OWNED BY public.api_processes.ap_id;


--
-- Name: api_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_settings (
    name character varying NOT NULL,
    value character varying NOT NULL
);


--
-- Name: api_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_users (
    user_id integer NOT NULL,
    deleted integer DEFAULT 0 NOT NULL,
    group_id integer DEFAULT 2 NOT NULL,
    user_name character varying(32) NOT NULL,
    full_name character varying DEFAULT ''::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    is_groupadmin boolean DEFAULT false NOT NULL,
    is_contentmanager boolean DEFAULT false NOT NULL,
    id uuid NOT NULL,
    email character varying(320) NOT NULL,
    hashed_password character varying(1024) NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    is_verified boolean NOT NULL,
    last_seen timestamp with time zone,
    CONSTRAINT ck_api_users_user_name_format CHECK ((((char_length((user_name)::text) >= 3) AND (char_length((user_name)::text) <= 32)) AND ((user_name)::text ~ '^[a-z0-9_-]+$'::text)))
);


--
-- Name: api_users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.api_users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: api_users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.api_users_user_id_seq OWNED BY public.api_users.user_id;


--
-- Name: api_vdb_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_vdb_status (
    avs_id integer NOT NULL,
    avs_type character varying NOT NULL,
    avs_url character varying NOT NULL,
    avs_collection character varying NOT NULL,
    avs_status character varying DEFAULT ''::character varying NOT NULL,
    avs_updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: api_vdb_status_avs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.api_vdb_status_avs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: api_vdb_status_avs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.api_vdb_status_avs_id_seq OWNED BY public.api_vdb_status.avs_id;


--
-- Name: doc_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.doc_tasks (
    doc_task_id integer NOT NULL,
    deleted integer DEFAULT 0 NOT NULL,
    group_id integer NOT NULL,
    user_id integer NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    status_text text DEFAULT ''::text NOT NULL,
    short_name character varying DEFAULT ''::character varying NOT NULL,
    input_text text NOT NULL,
    optional_text text DEFAULT ''::text NOT NULL,
    gvdbs_id integer NOT NULL,
    gvdbs_json text NOT NULL,
    gllms_id integer NOT NULL,
    gllms_json text NOT NULL,
    gc_id integer NOT NULL,
    context_json text,
    sent_to_llm text,
    output_text text,
    exc_text text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    fetched_at timestamp with time zone,
    context_at timestamp with time zone,
    completed_at timestamp with time zone,
    vdb_query_seconds double precision,
    llm_query_seconds double precision,
    llm_tokens_sent integer,
    llm_tokens_received integer,
    gvdbs_cfg_json text DEFAULT '{}'::text NOT NULL,
    output_text_2 text,
    question_number integer DEFAULT 1 NOT NULL
);


--
-- Name: doc_tasks_doc_task_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.doc_tasks_doc_task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: doc_tasks_doc_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.doc_tasks_doc_task_id_seq OWNED BY public.doc_tasks.doc_task_id;


--
-- Name: group_contexts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_contexts (
    gc_id integer NOT NULL,
    deleted integer DEFAULT 0 NOT NULL,
    group_id integer NOT NULL,
    gc_seqn integer NOT NULL,
    gc_name character varying NOT NULL,
    gc_text character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: group_contexts_gc_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_contexts_gc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_contexts_gc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_contexts_gc_id_seq OWNED BY public.group_contexts.gc_id;


--
-- Name: group_llms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_llms (
    gllms_id integer NOT NULL,
    deleted integer DEFAULT 0 NOT NULL,
    group_id integer NOT NULL,
    gllms_seqn integer NOT NULL,
    gllms_type public.gllms_type_enum NOT NULL,
    gllms_name character varying DEFAULT 'No LLM name'::character varying NOT NULL,
    gllms_api_base character varying NOT NULL,
    gllms_model character varying NOT NULL,
    gllms_api_key character varying NOT NULL,
    gllms_created_at timestamp with time zone DEFAULT now() NOT NULL,
    gllms_status character varying DEFAULT 'warning'::character varying NOT NULL,
    gllms_status_text character varying DEFAULT ''::character varying NOT NULL,
    gllms_status_updated_at timestamp with time zone,
    enabled boolean DEFAULT true NOT NULL
);


--
-- Name: group_llms_gllms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_llms_gllms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_llms_gllms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_llms_gllms_id_seq OWNED BY public.group_llms.gllms_id;


--
-- Name: group_vdbs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_vdbs (
    gvdbs_id integer NOT NULL,
    deleted integer DEFAULT 0 NOT NULL,
    group_id integer NOT NULL,
    gvdbs_seqn integer NOT NULL,
    gvdbs_type public.gvdbs_type_enum NOT NULL,
    gvdbs_name character varying DEFAULT 'No database name'::character varying NOT NULL,
    gvdbs_url character varying NOT NULL,
    gvdbs_collection character varying NOT NULL,
    gvdbs_emb_model character varying NOT NULL,
    gvdbs_created_at timestamp with time zone DEFAULT now() NOT NULL,
    gvdbs_status character varying DEFAULT 'warning'::character varying NOT NULL,
    gvdbs_status_text character varying DEFAULT ''::character varying NOT NULL,
    gvdbs_status_updated_at timestamp with time zone,
    enabled boolean DEFAULT true NOT NULL
);


--
-- Name: group_vdbs_gvdbs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_vdbs_gvdbs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_vdbs_gvdbs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_vdbs_gvdbs_id_seq OWNED BY public.group_vdbs.gvdbs_id;


--
-- Name: langchain_pg_collection; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.langchain_pg_collection (
    name character varying,
    cmetadata json,
    uuid uuid NOT NULL
);


--
-- Name: langchain_pg_embedding; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.langchain_pg_embedding (
    collection_id uuid,
    embedding public.vector,
    document character varying,
    cmetadata jsonb,
    custom_id character varying,
    uuid uuid NOT NULL
);


--
-- Name: log_crud; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.log_crud (
    lc_id integer NOT NULL,
    dt timestamp with time zone DEFAULT now() NOT NULL,
    group_id integer NOT NULL,
    user_id integer NOT NULL,
    user_name character varying NOT NULL,
    source_addr character varying NOT NULL,
    method character varying NOT NULL,
    dest_addr character varying NOT NULL,
    data character varying NOT NULL,
    result character varying
);


--
-- Name: log_crud_lc_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.log_crud_lc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: log_crud_lc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.log_crud_lc_id_seq OWNED BY public.log_crud.lc_id;


--
-- Name: api_groups group_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_groups ALTER COLUMN group_id SET DEFAULT nextval('public.api_groups_group_id_seq'::regclass);


--
-- Name: api_processes ap_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_processes ALTER COLUMN ap_id SET DEFAULT nextval('public.api_processes_ap_id_seq'::regclass);


--
-- Name: api_users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_users ALTER COLUMN user_id SET DEFAULT nextval('public.api_users_user_id_seq'::regclass);


--
-- Name: api_vdb_status avs_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_vdb_status ALTER COLUMN avs_id SET DEFAULT nextval('public.api_vdb_status_avs_id_seq'::regclass);


--
-- Name: doc_tasks doc_task_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_tasks ALTER COLUMN doc_task_id SET DEFAULT nextval('public.doc_tasks_doc_task_id_seq'::regclass);


--
-- Name: group_contexts gc_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_contexts ALTER COLUMN gc_id SET DEFAULT nextval('public.group_contexts_gc_id_seq'::regclass);


--
-- Name: group_llms gllms_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_llms ALTER COLUMN gllms_id SET DEFAULT nextval('public.group_llms_gllms_id_seq'::regclass);


--
-- Name: group_vdbs gvdbs_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_vdbs ALTER COLUMN gvdbs_id SET DEFAULT nextval('public.group_vdbs_gvdbs_id_seq'::regclass);


--
-- Name: log_crud lc_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.log_crud ALTER COLUMN lc_id SET DEFAULT nextval('public.log_crud_lc_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: api_processes ap_uix; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_processes
    ADD CONSTRAINT ap_uix UNIQUE (ap_name, ap_subname);


--
-- Name: api_groups api_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_groups
    ADD CONSTRAINT api_groups_pkey PRIMARY KEY (group_id);


--
-- Name: api_processes api_processes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_processes
    ADD CONSTRAINT api_processes_pkey PRIMARY KEY (ap_id);


--
-- Name: api_settings api_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_settings
    ADD CONSTRAINT api_settings_pkey PRIMARY KEY (name);


--
-- Name: api_users api_users_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_users
    ADD CONSTRAINT api_users_id_key UNIQUE (id);


--
-- Name: api_users api_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_users
    ADD CONSTRAINT api_users_pkey PRIMARY KEY (user_id);


--
-- Name: api_vdb_status api_vdb_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_vdb_status
    ADD CONSTRAINT api_vdb_status_pkey PRIMARY KEY (avs_id);


--
-- Name: api_vdb_status avs_uix; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_vdb_status
    ADD CONSTRAINT avs_uix UNIQUE (avs_type, avs_url, avs_collection);


--
-- Name: doc_tasks doc_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_tasks
    ADD CONSTRAINT doc_tasks_pkey PRIMARY KEY (doc_task_id);


--
-- Name: group_contexts group_contexts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_contexts
    ADD CONSTRAINT group_contexts_pkey PRIMARY KEY (gc_id);


--
-- Name: group_llms group_llms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_llms
    ADD CONSTRAINT group_llms_pkey PRIMARY KEY (gllms_id);


--
-- Name: group_vdbs group_vdbs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_vdbs
    ADD CONSTRAINT group_vdbs_pkey PRIMARY KEY (gvdbs_id);


--
-- Name: langchain_pg_collection langchain_pg_collection_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.langchain_pg_collection
    ADD CONSTRAINT langchain_pg_collection_pkey PRIMARY KEY (uuid);


--
-- Name: langchain_pg_embedding langchain_pg_embedding_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.langchain_pg_embedding
    ADD CONSTRAINT langchain_pg_embedding_pkey PRIMARY KEY (uuid);


--
-- Name: log_crud log_crud_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.log_crud
    ADD CONSTRAINT log_crud_pkey PRIMARY KEY (lc_id);


--
-- Name: api_users uq_api_users_user_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_users
    ADD CONSTRAINT uq_api_users_user_name UNIQUE (user_name);


--
-- Name: ix_api_groups_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_api_groups_deleted ON public.api_groups USING btree (deleted);


--
-- Name: ix_api_users_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_api_users_deleted ON public.api_users USING btree (deleted);


--
-- Name: ix_api_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_api_users_email ON public.api_users USING btree (email);


--
-- Name: ix_cmetadata_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_cmetadata_gin ON public.langchain_pg_embedding USING gin (cmetadata jsonb_path_ops);


--
-- Name: ix_doc_tasks_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_doc_tasks_created_at ON public.doc_tasks USING btree (created_at);


--
-- Name: ix_doc_tasks_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_doc_tasks_deleted ON public.doc_tasks USING btree (deleted);


--
-- Name: ix_doc_tasks_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_doc_tasks_user_id ON public.doc_tasks USING btree (user_id);


--
-- Name: ix_group_contexts_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_group_contexts_deleted ON public.group_contexts USING btree (deleted);


--
-- Name: ix_group_llms_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_group_llms_deleted ON public.group_llms USING btree (deleted);


--
-- Name: ix_group_llms_enabled; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_group_llms_enabled ON public.group_llms USING btree (enabled);


--
-- Name: ix_group_llms_group_id_seqn; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_group_llms_group_id_seqn ON public.group_llms USING btree (group_id, gllms_seqn);


--
-- Name: ix_group_vdbs_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_group_vdbs_deleted ON public.group_vdbs USING btree (deleted);


--
-- Name: ix_group_vdbs_enabled; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_group_vdbs_enabled ON public.group_vdbs USING btree (enabled);


--
-- Name: ix_group_vdbs_group_id_seqn; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_group_vdbs_group_id_seqn ON public.group_vdbs USING btree (group_id, gvdbs_seqn);


--
-- Name: doc_tasks doc_tasks_gc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_tasks
    ADD CONSTRAINT doc_tasks_gc_id_fkey FOREIGN KEY (gc_id) REFERENCES public.group_contexts(gc_id);


--
-- Name: api_users fk_api_users_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_users
    ADD CONSTRAINT fk_api_users_group_id FOREIGN KEY (group_id) REFERENCES public.api_groups(group_id);


--
-- Name: doc_tasks fk_api_users_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_tasks
    ADD CONSTRAINT fk_api_users_group_id FOREIGN KEY (group_id) REFERENCES public.api_groups(group_id);


--
-- Name: group_contexts fk_group_contexts_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_contexts
    ADD CONSTRAINT fk_group_contexts_group_id FOREIGN KEY (group_id) REFERENCES public.api_groups(group_id);


--
-- Name: group_llms fk_group_llms_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_llms
    ADD CONSTRAINT fk_group_llms_group_id FOREIGN KEY (group_id) REFERENCES public.api_groups(group_id);


--
-- Name: group_vdbs fk_group_vdbs_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_vdbs
    ADD CONSTRAINT fk_group_vdbs_group_id FOREIGN KEY (group_id) REFERENCES public.api_groups(group_id);


--
-- Name: langchain_pg_embedding langchain_pg_embedding_collection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.langchain_pg_embedding
    ADD CONSTRAINT langchain_pg_embedding_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES public.langchain_pg_collection(uuid) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict f45GTMSaaGlrm7Z9HCxAmpBRvIbQ8ue8WSttB6x2xsulxCfNx6QLbfIbeGi4s7D

