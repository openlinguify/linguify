#!/usr/bin/env python3
"""
Quick script to fix sequence issues without needing Django environment
This creates a simple SQL script that you can copy-paste into pgAdmin or psql
"""

def generate_sql_fix():
    tables = [
        'authentication_user',
        'notification_notificationsetting',
        'notification_notification',
        'notification_notificationdevice'
    ]
    
    sql_commands = [
        "-- Quick fix for PostgreSQL sequence issues",
        "-- Copy and paste this into pgAdmin or run with psql",
        "",
    ]
    
    for table in tables:
        sql_commands.extend([
            f"-- Fix {table} sequence",
            f"DO $$",
            f"DECLARE",
            f"    max_id INTEGER;",
            f"    sequence_name TEXT;",
            f"BEGIN",
            f"    -- Get max ID, handling empty tables",
            f"    BEGIN",
            f"        SELECT COALESCE(MAX(id), 0) INTO max_id FROM {table};",
            f"    EXCEPTION",
            f"        WHEN undefined_table THEN",
            f"            RAISE NOTICE 'Table {table} does not exist, skipping...';",
            f"            RETURN;",
            f"    END;",
            f"    ",
            f"    -- Check if sequence exists",
            f"    SELECT pg_get_serial_sequence('{table}', 'id') INTO sequence_name;",
            f"    ",
            f"    IF sequence_name IS NOT NULL THEN",
            f"        -- Reset existing sequence",
            f"        PERFORM setval(sequence_name, max_id + 1, false);",
            f"        RAISE NOTICE 'Fixed sequence for {table}: set to %', max_id + 1;",
            f"    ELSE",
            f"        -- Create new sequence",
            f"        sequence_name := '{table}_id_seq';",
            f"        EXECUTE format('CREATE SEQUENCE IF NOT EXISTS %I AS integer START 1 INCREMENT 1', sequence_name);",
            f"        PERFORM setval(sequence_name, max_id + 1, false);",
            f"        EXECUTE format('ALTER TABLE {table} ALTER COLUMN id SET DEFAULT nextval(%L)', sequence_name);",
            f"        EXECUTE format('ALTER SEQUENCE %I OWNED BY {table}.id', sequence_name);",
            f"        RAISE NOTICE 'Created and fixed sequence for {table}: set to %', max_id + 1;",
            f"    END IF;",
            f"END $$;",
            "",
        ])
    
    sql_commands.append("-- All sequences fixed! You can now test user registration.")
    
    return "\n".join(sql_commands)

if __name__ == "__main__":
    print("Generating SQL fix script...")
    sql_content = generate_sql_fix()
    
    # Write to file
    with open('fix_sequences_generated.sql', 'w') as f:
        f.write(sql_content)
    
    print("✅ SQL script generated: fix_sequences_generated.sql")
    print("\nTo fix the sequences, you can either:")
    print("1. Run: psql -d your_database_name -f fix_sequences_generated.sql")
    print("2. Copy the SQL below and paste it into pgAdmin Query Tool:")
    print("\n" + "="*50)
    print(sql_content)
    print("="*50)