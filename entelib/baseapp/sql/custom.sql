ALTER TABLE auth_user ADD CONSTRAINT email_must_be_unique UNIQUE (email);

CREATE LANGUAGE plpgsql;

CREATE FUNCTION active_user_will_not_await_activation () RETURNS opaque AS '
BEGIN
    IF NEW.is_active THEN
        UPDATE baseapp_userprofile SET awaits_activation = FALSE
        WHERE user_id = NEW.id;
    END IF;
    RETURN NEW;
END;
' LANGUAGE 'plpgsql';


CREATE TRIGGER user_activated
    AFTER INSERT OR UPDATE
    ON auth_user FOR EACH ROW
    EXECUTE PROCEDURE active_user_will_not_await_activation();
