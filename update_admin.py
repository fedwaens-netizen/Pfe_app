from db.database import engine
from sqlalchemy import text
with engine.connect() as con:
    con.execute(text("UPDATE users SET is_admin = true WHERE username = 'admin'"))
    con.commit()
print("Admin updated")
