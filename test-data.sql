--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.2
-- Dumped by pg_dump version 9.6.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

--
-- Data for Name: activity_type; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY activity_type (id, name) FROM stdin;
\.


--
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY app_user (username, name, email, password_hash, salt, last_logged_in) FROM stdin;
\.


--
-- Data for Name: disease; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY disease (id, name) FROM stdin;
disease-1	disease-1
disease-2	disease-2
\.


--
-- Data for Name: modelling_group; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY modelling_group (id, description, current) FROM stdin;
group-1	description	\N
\.


--
-- Data for Name: model; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY model (id, modelling_group, description, citation, current) FROM stdin;
\.


--
-- Data for Name: model_version; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY model_version (id, model, version, note, fingerprint) FROM stdin;
\.


--
-- Data for Name: responsibility_set_status; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY responsibility_set_status (id, name) FROM stdin;
submitted	submitted
\.


--
-- Data for Name: touchstone_name; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY touchstone_name (id, description) FROM stdin;
touchstone	Touchstone v1
\.


--
-- Data for Name: touchstone_status; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY touchstone_status (id, name) FROM stdin;
open	open
\.


--
-- Data for Name: touchstone; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY touchstone (id, touchstone_name, version, description, status, year_start, year_end) FROM stdin;
touchstone-1	touchstone	1	Touchstone v1	open	1900	2000
touchstone-2	touchstone	2	Touchstone v2	open	1900	2000
\.


--
-- Data for Name: responsibility_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY responsibility_set (id, modelling_group, touchstone, status) FROM stdin;
1	group-1	touchstone-1	submitted
\.


--
-- Data for Name: scenario_description; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY scenario_description (id, description, disease) FROM stdin;
scenario-1	description 1	disease-1
scenario-2	description 2	disease-2
\.


--
-- Data for Name: scenario; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY scenario (id, touchstone, scenario_description) FROM stdin;
1	touchstone-1	scenario-1
2	touchstone-1	scenario-2
\.


--
-- Data for Name: responsibility; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY responsibility (id, responsibility_set, scenario) FROM stdin;
1	1	1
2	1	2
\.


--
-- Data for Name: burden_estimate_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY burden_estimate_set (id, model_version, responsibility, run_info, validation, comment, interpolated, complete, uploaded_by, uploaded_on) FROM stdin;
\.


--
-- Data for Name: country; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY country (id, name) FROM stdin;
\.


--
-- Data for Name: outcome; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY outcome (id, code, name) FROM stdin;
\.


--
-- Data for Name: burden_estimate; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY burden_estimate (id, burden_estimate_set, country, year, outcome, stochastic, value) FROM stdin;
\.


--
-- Name: burden_estimate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('burden_estimate_id_seq', 1, false);


--
-- Name: burden_estimate_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('burden_estimate_set_id_seq', 1, false);


--
-- Data for Name: gavi_support_level; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY gavi_support_level (id, name) FROM stdin;
\.


--
-- Data for Name: vaccine; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY vaccine (id, name) FROM stdin;
\.


--
-- Data for Name: coverage_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY coverage_set (id, name, touchstone, vaccine, gavi_support_level, activity_type) FROM stdin;
\.


--
-- Data for Name: coverage; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY coverage (id, coverage_set, year, country, age_from, age_to, age_to_exclusive, age_range_verbatim, coverage, gavi_support, activity) FROM stdin;
\.


--
-- Name: coverage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('coverage_id_seq', 1, false);


--
-- Name: coverage_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('coverage_set_id_seq', 1, false);


--
-- Data for Name: impact_estimate_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate_set (id, version, name, script) FROM stdin;
\.


--
-- Data for Name: impact_estimate; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate (id, impact_estimate_set, year, country, value) FROM stdin;
\.


--
-- Data for Name: impact_estimate_components; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate_components (id, burden_estimate_set, impact_estimate_set, outcome, name) FROM stdin;
\.


--
-- Name: impact_estimate_components_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_components_id_seq', 1, false);


--
-- Name: impact_estimate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_id_seq', 1, false);


--
-- Name: impact_estimate_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_set_id_seq', 1, false);


--
-- Name: model_version_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('model_version_id_seq', 1, false);


--
-- Name: outcome_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('outcome_id_seq', 1, false);


--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY permission (name) FROM stdin;
\.


--
-- Name: responsibility_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('responsibility_id_seq', 2, true);


--
-- Name: responsibility_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('responsibility_set_id_seq', 1, true);


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY role (id, name, scope_prefix, description) FROM stdin;
\.


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('role_id_seq', 1, false);


--
-- Data for Name: role_permission; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY role_permission (role, permission) FROM stdin;
\.


--
-- Data for Name: scenario_coverage_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY scenario_coverage_set (id, scenario, coverage_set, "order") FROM stdin;
\.


--
-- Name: scenario_coverage_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('scenario_coverage_set_id_seq', 1, false);


--
-- Name: scenario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('scenario_id_seq', 2, true);


--
-- Data for Name: touchstone_country; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY touchstone_country (id, touchstone, country, who_region, gavi73, wuenic) FROM stdin;
\.


--
-- Name: touchstone_country_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('touchstone_country_id_seq', 1, false);


--
-- Data for Name: user_role; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY user_role (username, role, scope_id) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

