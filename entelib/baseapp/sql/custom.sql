ALTER TABLE auth_user ADD CONSTRAINT email_must_be_unique UNIQUE (email);
