CREATE TABLE keys (
    uuid UUID PRIMARY KEY,
    hostname VARCHAR NOT NULL,
    port INTEGER NOT NULL,
    password VARCHAR NOT NULL,
    method VARCHAR NOT NULL
);