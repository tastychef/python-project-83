CREATE TABLE IF NOT EXISTS urls(
    id bigint GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at timestamp DEFAULT now(),
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS url_checks(
    id bigint GENERATED ALWAYS AS IDENTITY,
    url_id bigint,
    status_code int,
    h1 varchar(550),
    title varchar(550),
    description varchar(550),
    created_at timestamp DEFAULT now(),
    PRIMARY KEY(id),
    CONSTRAINT url_checks_urls_id_fk
        FOREIGN KEY(url_id)
        REFERENCES urls(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
