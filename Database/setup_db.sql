CREATE DATABASE covid_database;

\c covid_database

CREATE USER covid_user WITH PASSWORD 'covid_password';
GRANT ALL PRIVILEGES ON DATABASE covid_database TO covid_user;

-- Create and fill location table
CREATE TABLE Location (
    l_nationname VARCHAR(100),
    l_nationkey VARCHAR(10) PRIMARY KEY,
    l_last_observation_date DATE,
    l_source_name VARCHAR(255),
    l_source_website VARCHAR(255)
);

\COPY location (l_nationname, l_nationkey, l_last_observation_date, l_source_name, l_source_website) FROM 'Data/locations.csv' DELIMITER ',' CSV HEADER;

-- Create and fill cases table
CREATE TABLE Cases (
 	c_nationkey VARCHAR(10),
 	c_date DATE,
	c_cases BIGINT,
	PRIMARY KEY (c_nationkey, c_date),
 	FOREIGN KEY (c_nationkey) REFERENCES public.location(l_nationkey) ON DELETE CASCADE
);

\COPY cases (c_nationkey, c_date, c_cases) FROM 'Data/cases.csv' DELIMITER ',';

-- Create and fill deaths table
CREATE TABLE Deaths (
 	d_nationkey VARCHAR(10),
 	d_date DATE,
	d_death BIGINT,
	PRIMARY KEY (d_nationkey, d_date),
 	FOREIGN KEY (d_nationkey) REFERENCES public.location(l_nationkey) ON DELETE CASCADE
);

\COPY deaths (d_nationkey, d_date, d_death) FROM 'Data/deaths.csv' DELIMITER ',';

-- Create and fill testing table
CREATE TABLE Testing (
    t_entity VARCHAR(100),
    t_nationkey VARCHAR(10),
    t_date DATE,
    t_cumulative_total NUMERIC,
    t_daily_change_ct NUMERIC,
    t_ct_per_thousand NUMERIC,
    t_daily_change_ct_per_thousand NUMERIC,
    t_short_term_positive_rate NUMERIC,
    t_short_term_tests_per_case NUMERIC,
    PRIMARY KEY (t_nationkey, t_date),
    FOREIGN KEY (t_nationkey) REFERENCES public.location(l_nationkey) ON DELETE CASCADE
);

\COPY testing (t_entity, t_nationkey, t_date, t_cumulative_total, t_daily_change_ct, t_ct_per_thousand, t_daily_change_ct_per_thousand, t_short_term_positive_rate, t_short_term_tests_per_case) FROM 'Data/testing.csv' DELIMITER ',' CSV HEADER;

-- Create and fill hospitalizations table
CREATE TABLE Hospitalizations (
    h_nationname VARCHAR(100),
    h_nationkey VARCHAR(10),
    h_date DATE,
    h_indicator VARCHAR(100),
    h_value NUMERIC,
    PRIMARY KEY (h_date, h_nationkey, h_indicator),
    FOREIGN KEY (h_nationkey) REFERENCES public.location(l_nationkey) ON DELETE CASCADE
);

\COPY hospitalizations (h_nationname, h_nationkey, h_date, h_indicator, h_value) FROM 'Data/hospitalizations.csv' DELIMITER ',' CSV HEADER;

-- Create and fill vaccinations table
CREATE TABLE Vaccinations (
    v_nationname VARCHAR(100),
    v_nationkey VARCHAR(10), 
    v_date DATE,
    v_total_vaccinations BIGINT,
    v_people_fully_vaccinated BIGINT,
    v_total_boosters BIGINT,
    v_daily_vaccinations BIGINT,
    v_people_fully_vaccinated_per_hundred NUMERIC,
    v_total_boosters_per_hundred NUMERIC,
    PRIMARY KEY (v_nationkey, v_date),
    FOREIGN KEY (v_nationkey) REFERENCES public.location(l_nationkey) ON DELETE CASCADE 
);

\COPY vaccinations (v_nationname, v_nationkey, v_date, v_total_vaccinations, v_people_fully_vaccinated, v_total_boosters, v_daily_vaccinations, v_people_fully_vaccinated_per_hundred, v_total_boosters_per_hundred) FROM 'Data/vaccinations.csv' DELIMITER ',' CSV HEADER;

-- Grant permissions on all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO covid_user;
