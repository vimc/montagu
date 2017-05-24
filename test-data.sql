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
none	none
routine	routine
campaign	campaign
\.


--
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY app_user (username, name, email, password_hash, salt, last_logged_in) FROM stdin;
\.


--
-- Data for Name: modelling_group; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY modelling_group (id, description, current) FROM stdin;
IC-Garske	Imperial Yellow Fever modelling group	\N
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
-- Data for Name: burden_estimate_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY burden_estimate_set (id, model_version, responsibility, run_info, validation, comment, interpolated, complete, uploaded_by, uploaded_on) FROM stdin;
\.


--
-- Data for Name: burden_outcome; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY burden_outcome (id, code, name) FROM stdin;
\.


--
-- Data for Name: country; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY country (id, name) FROM stdin;
\.


--
-- Data for Name: burden_estimate; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY burden_estimate (id, burden_estimate_set, country, year, burden_outcome, stochastic, value) FROM stdin;
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
-- Data for Name: burden_estimate_set_problem; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY burden_estimate_set_problem (id, burden_estimate_set, problem) FROM stdin;
\.


--
-- Name: burden_estimate_set_problem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('burden_estimate_set_problem_id_seq', 1, false);


--
-- Name: burden_outcome_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('burden_outcome_id_seq', 1, false);


--
-- Data for Name: gavi_support_level; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY gavi_support_level (id, name) FROM stdin;
none	none
without	without
with	with
\.


--
-- Data for Name: touchstone_name; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY touchstone_name (id, description) FROM stdin;
op-2017	Operational Forecast 2017
\.


--
-- Data for Name: touchstone_status; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY touchstone_status (id, name) FROM stdin;
finished	finished
open	open
\.


--
-- Data for Name: touchstone; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY touchstone (id, touchstone_name, version, description, status, year_start, year_end) FROM stdin;
op-2017-1	op-2017	1	Operational Forecast 2017 (v1)	finished	1900	2000
op-2017-2	op-2017	2	Operational Forecast 2017 (v2)	open	1900	2000
\.


--
-- Data for Name: vaccine; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY vaccine (id, name) FROM stdin;
YF	Yellow Fever
\.


--
-- Data for Name: coverage_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY coverage_set (id, name, touchstone, vaccine, gavi_support_level, activity_type) FROM stdin;
1	Yellow Fever, no vaccination	op-2017-2	YF	none	none
2	Yellow Fever, routine, without GAVI	op-2017-2	YF	without	routine
3	Yellow Fever, routine, with GAVI	op-2017-2	YF	with	routine
4	Yellow Fever, campaign, without GAVI	op-2017-2	YF	without	campaign
5	Yellow Fever, campaign, with GAVI	op-2017-2	YF	with	campaign
\.


--
-- Data for Name: coverage; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY coverage (id, coverage_set, year, country, age_from, age_to, age_range_verbatim, coverage, target, gavi_support, activity) FROM stdin;
\.


--
-- Name: coverage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('coverage_id_seq', 1, false);


--
-- Name: coverage_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('coverage_set_id_seq', 5, true);


--
-- Data for Name: disease; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY disease (id, name) FROM stdin;
YF	Yellow Fever
\.


--
-- Data for Name: impact_outcome; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_outcome (id, name) FROM stdin;
\.


--
-- Data for Name: responsibility_set_status; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY responsibility_set_status (id, name) FROM stdin;
incomplete	incomplete
\.


--
-- Data for Name: responsibility_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY responsibility_set (id, modelling_group, touchstone, status) FROM stdin;
1	IC-Garske	op-2017-2	incomplete
\.


--
-- Data for Name: support_type; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY support_type (id, name) FROM stdin;
\.


--
-- Data for Name: impact_estimate_recipe; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate_recipe (id, version, responsibility_set, name, script, comment, impact_outcome, activity_type, support_type, disease, vaccine) FROM stdin;
\.


--
-- Data for Name: impact_estimate_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate_set (id, impact_estimate_recipe, computed_on) FROM stdin;
\.


--
-- Data for Name: impact_estimate; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate (id, impact_estimate_set, year, country, value) FROM stdin;
\.


--
-- Name: impact_estimate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_id_seq', 1, false);


--
-- Data for Name: scenario_description; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY scenario_description (id, description, disease) FROM stdin;
yf-routine	Yellow Fever, routine	YF
yf-campaign	Yellow Fever, campaign	YF
\.


--
-- Data for Name: scenario; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY scenario (id, touchstone, scenario_description) FROM stdin;
1	op-2017-2	yf-routine
2	op-2017-2	yf-campaign
\.


--
-- Data for Name: responsibility; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY responsibility (id, responsibility_set, scenario, current_burden_estimate_set) FROM stdin;
1	1	1	\N
2	1	2	\N
\.


--
-- Data for Name: impact_estimate_ingredient; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate_ingredient (id, impact_estimate_recipe, responsibility, burden_outcome, name) FROM stdin;
\.


--
-- Name: impact_estimate_ingredient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_ingredient_id_seq', 1, false);


--
-- Name: impact_estimate_recipe_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_recipe_id_seq', 1, false);


--
-- Name: impact_estimate_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_set_id_seq', 1, false);


--
-- Data for Name: impact_estimate_set_ingredient; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY impact_estimate_set_ingredient (id, impact_estimate_set, impact_estimate_ingredient, burden_estimate_set) FROM stdin;
\.


--
-- Name: impact_estimate_set_ingredient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('impact_estimate_set_ingredient_id_seq', 1, false);


--
-- Name: model_version_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('model_version_id_seq', 1, false);


--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY permission (name) FROM stdin;
can-login
scenarios.read
countries.read
modelling-groups.read
models.read
touchstones.read
responsibilities.read
users.read
estimates.read
diseases.write
vaccines.write
scenarios.write
countries.write
touchstones.prepare
responsibilities.write
coverage.read
touchstones.open
coverage.write
users.create
users.edit-all
roles.read
roles.write
modelling-groups.write
estimates.review
estimates.read-unfinished
estimates.write
estimates.submit
modelling-groups.manage-members
models.write
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
1	user	\N	Log in
2	touchstone-preparer	\N	Prepare touchstones
3	touchstone-reviewer	\N	Review touchstones before marking as 'open'
4	coverage-provider	\N	Upload coverage data
5	user-manager	\N	Manage users and permissions
6	estimates-reviewer	\N	Review uploaded burden estimates
7	member	modelling-group	Member of the group
8	uploader	modelling-group	Upload burden estimates
9	submitter	modelling-group	Mark burden estimates as complete
10	user-manager	modelling-group	Manage group members and permissions
11	model-manager	modelling-group	Add new models and model versions
\.


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('role_id_seq', 11, true);


--
-- Data for Name: role_permission; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY role_permission (role, permission) FROM stdin;
1	can-login
1	scenarios.read
1	countries.read
1	modelling-groups.read
1	models.read
1	touchstones.read
1	responsibilities.read
1	users.read
1	estimates.read
2	diseases.write
2	vaccines.write
2	scenarios.write
2	countries.write
2	touchstones.prepare
2	responsibilities.write
2	coverage.read
3	touchstones.open
3	coverage.read
4	coverage.read
4	coverage.write
5	users.create
5	users.edit-all
5	roles.read
5	roles.write
5	modelling-groups.write
6	estimates.review
6	estimates.read-unfinished
7	estimates.read-unfinished
7	coverage.read
8	estimates.write
9	estimates.submit
10	modelling-groups.manage-members
10	users.create
10	roles.write
11	models.write
\.


--
-- Data for Name: scenario_coverage_set; Type: TABLE DATA; Schema: public; Owner: vimc
--

COPY scenario_coverage_set (id, scenario, coverage_set, "order") FROM stdin;
1	1	1	0
2	1	2	1
3	1	3	2
4	2	1	0
5	2	2	1
6	2	3	2
7	2	4	3
8	2	5	4
\.


--
-- Name: scenario_coverage_set_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vimc
--

SELECT pg_catalog.setval('scenario_coverage_set_id_seq', 8, true);


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

