import csv
import json
from connect import get_connection


def run_sql_file(filename):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        cur.execute(file.read())

    conn.commit()
    cur.close()
    conn.close()


def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group_name = input("Group (Family/Work/Friend/Other): ")
    phone = input("Phone: ")
    phone_type = input("Type (home/work/mobile): ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    group = cur.fetchone()

    if group is None:
        print("Group not found")
    else:
        group_id = group[0]

        cur.execute(
            """
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, email, birthday, group_id)
        )

        contact_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO phones(contact_id, phone, type)
            VALUES (%s, %s, %s)
            """,
            (contact_id, phone, phone_type)
        )

        conn.commit()
        print("Contact added")

    cur.close()
    conn.close()


def show_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT c.id, c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY c.id
        """
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def search_contact():
    query = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def filter_by_group():
    group_name = input("Group name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s
        """,
        (group_name,)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def sort_contacts():
    print("1 - Sort by name")
    print("2 - Sort by birthday")

    choice = input("Choose: ")

    if choice == "1":
        order_by = "c.name"
    elif choice == "2":
        order_by = "c.birthday"
    else:
        print("Invalid choice")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order_by}
        """
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_contact():
    contact_id = input("Contact id: ")
    new_name = input("New name: ")
    new_email = input("New email: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE contacts
        SET name = %s, email = %s
        WHERE id = %s
        """,
        (new_name, new_email, contact_id)
    )

    conn.commit()
    print("Contact updated")

    cur.close()
    conn.close()


def delete_contact():
    contact_id = input("Contact id: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))

    conn.commit()
    print("Contact deleted")

    cur.close()
    conn.close()


def add_phone_to_contact():
    name = input("Contact name: ")
    phone = input("Phone: ")
    phone_type = input("Type (home/work/mobile): ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))

    conn.commit()
    print("Phone added")

    cur.close()
    conn.close()


def move_contact_to_group():
    name = input("Contact name: ")
    group_name = input("New group: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL move_to_group(%s, %s)", (name, group_name))

    conn.commit()
    print("Contact moved")

    cur.close()
    conn.close()


def export_to_json():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT c.id, c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY c.id
        """
    )

    rows = cur.fetchall()

    contacts = []

    for row in rows:
        contacts.append({
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "birthday": str(row[3]),
            "group": row[4],
            "phone": row[5],
            "type": row[6]
        })

    with open("contacts.json", "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4)

    print("Exported to contacts.json")

    cur.close()
    conn.close()


def import_from_csv():
    conn = get_connection()
    cur = conn.cursor()

    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cur.execute("SELECT id FROM groups WHERE name = %s", (row["group_name"],))
            group = cur.fetchone()

            if group is None:
                continue

            group_id = group[0]

            cur.execute(
                """
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (row["name"], row["email"], row["birthday"], group_id)
            )

            contact_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                """,
                (contact_id, row["phone"], row["type"])
            )

    conn.commit()
    print("Imported from CSV")

    cur.close()
    conn.close()


def menu():
    while True:
        print("\nPHONEBOOK MENU")
        print("1 - Create tables")
        print("2 - Create procedures")
        print("3 - Add contact")
        print("4 - Show contacts")
        print("5 - Search contact")
        print("6 - Filter by group")
        print("7 - Sort contacts")
        print("8 - Update contact")
        print("9 - Delete contact")
        print("10 - Add phone to contact")
        print("11 - Move contact to group")
        print("12 - Export to JSON")
        print("13 - Import from CSV")
        print("0 - Exit")

        choice = input("Choose: ")

        if choice == "1":
            run_sql_file("schema.sql")
        elif choice == "2":
            run_sql_file("procedures.sql")
        elif choice == "3":
            add_contact()
        elif choice == "4":
            show_contacts()
        elif choice == "5":
            search_contact()
        elif choice == "6":
            filter_by_group()
        elif choice == "7":
            sort_contacts()
        elif choice == "8":
            update_contact()
        elif choice == "9":
            delete_contact()
        elif choice == "10":
            add_phone_to_contact()
        elif choice == "11":
            move_contact_to_group()
        elif choice == "12":
            export_to_json()
        elif choice == "13":
            import_from_csv()
        elif choice == "0":
            break
        else:
            print("Invalid choice")


menu()