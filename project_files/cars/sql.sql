create table items
(
    website                       TEXT,
    website_id                    TEXT,
    price                         REAL,
    heading                       TEXT,
    link                          TEXT,
    img_link                      TEXT,
    make                          TEXT,
    model                         TEXT,
    odometer_km                   REAL,
    year                          REAL,
    colours                       TEXT,
    area                          TEXT,
    dealer                        TEXT,
    dealer_location               TEXT,
    dealer_link                   TEXT,
    engine_power_max_kW           REAL,
    engine_size_l                 REAL,
    engine_fuel_type              TEXT,
    engine_fuel_tank_l            REAL,
    engine_transmission           TEXT,
    performace_0_to_100_s         REAL,
    performace_speed_max_kmph     REAL,
    economy_fuel_consumption_lpkm REAL,
    economy_fuel_range_km         REAL,
    economy_CO2_gpkm              REAL,
    safety_ABS                    INTEGER,
    safety_EBD                    INTEGER,
    safety_brake_assist           INTEGER,
    safety_driver_airbag          INTEGER,
    safety_passenger_airbag       INTEGER,
    safety_airbag_quantity        INTEGER,
    features_bluetooth            INTEGER,
    features_aircon               INTEGER,
    specs_doors                   REAL,
    specs_seats                   REAL,
    specs_kerb_weight             REAL,
    options                       TEXT,
    specs_central_locking         TEXT,
    description                   TEXT
);



CREATE TABLE dates
(
    website       TEXT,
    website_id    TEXT,
    date_accessed TEXT
);