CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Contact not found';
    ELSE
        INSERT INTO phones(contact_id, phone, type)
        VALUES (v_contact_id, p_phone, p_type);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INT;
BEGIN
    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    IF v_group_id IS NULL THEN
        RAISE NOTICE 'Group not found';
    ELSE
        UPDATE contacts
        SET group_id = v_group_id
        WHERE name = p_contact_name;
    END IF;
END;
$$;


CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INT,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone VARCHAR,
    phone_type VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name,
        p.phone,
        p.type
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE 
        c.name ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%';
END;
$$;