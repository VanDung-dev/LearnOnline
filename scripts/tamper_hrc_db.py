import sqlite3
import json
import os

db_path = "data/course_certificates/hierachain.db"

def main():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Print existing event
    cursor.execute("SELECT id, data FROM events WHERE entity_id = 'taO5rmLlnzmC'")
    row = cursor.fetchone()
    if not row:
        print("Target certificate event not found. Checking all events:")
        cursor.execute("SELECT id, entity_id, data FROM events WHERE event_type = 'certificate_issued'")
        for r in cursor.fetchall():
            print(f"ID: {r[0]}, Entity: {r[1]}, Data: {r[2]}")
        conn.close()
        return
        
    event_id, data_str = row
    data = json.loads(data_str)
    print(f"\n--- Original Event (ID: {event_id}) ---")
    print(json.dumps(data, indent=2))
    
    # 2. Tamper with the student name
    data["details"]["student_name"] = "Hacker Eve"
    tampered_data_str = json.dumps(data)
    
    cursor.execute("UPDATE events SET data = ? WHERE id = ?", (tampered_data_str, event_id))
    conn.commit()
    print(f"\n--- Tampered Event (ID: {event_id}) saved ---")
    
    # 3. Print verified change in DB
    cursor.execute("SELECT id, data FROM events WHERE id = ?", (event_id,))
    tampered_row = cursor.fetchone()
    print(json.dumps(json.loads(tampered_row[1]), indent=2))
    
    conn.close()

if __name__ == "__main__":
    main()
