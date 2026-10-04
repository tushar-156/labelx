from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Ensure .env is loaded from backend directory regardless of cwd
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# Example format: postgresql://user:password@endpoint.neon.tech/dbname
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    db_file = os.path.join(base_dir, "local_records.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_file}"

# Neon recommends sslmode=require for postgresql
if SQLALCHEMY_DATABASE_URL.startswith("postgres"):
    if "sslmode=" not in SQLALCHEMY_DATABASE_URL:
        if "?" in SQLALCHEMY_DATABASE_URL:
            SQLALCHEMY_DATABASE_URL += "&sslmode=require"
        else:
            SQLALCHEMY_DATABASE_URL += "?sslmode=require"

# Engine configuration with automatic pre-ping and recycle
# to prevent "SSL connection has been closed unexpectedly" on idle Neon connections
engine_kwargs = {
    "pool_pre_ping": True,  # Checks connection liveness before executing queries
    "pool_recycle": 280,    # Automatically refreshes connections before Neon's 5-minute pooler idle timeout
}

if SQLALCHEMY_DATABASE_URL.startswith("postgres"):
    engine_kwargs["connect_args"] = {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
elif SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
    # Eagerly verify connection so offline / DNS / SSL blocks fall back to SQLite immediately
    if SQLALCHEMY_DATABASE_URL.startswith("postgres"):
        with engine.connect() as test_conn:
            pass
except Exception as e:
    print(f"Notice: Remote database unavailable ({e}). Automatically switching to resilient local SQLite.")
    db_file = os.path.join(base_dir, "local_records.db")
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fallback SQLite session maker if Postgres fails at runtime
db_file = os.path.join(base_dir, "local_records.db")
FallbackSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
)

Base = declarative_base()

# Auto-ensure tables exist on active engine and fallback SQLite
def init_db():
    try:
        from . import models
        Base.metadata.create_all(bind=engine)
        # Also ensure local fallback tables exist
        fallback_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=fallback_engine)
    except Exception as e:
        print(f"Notice: Database initialization notice ({e})")

init_db()

def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(f"Notice: Primary DB session failed ({e}), routing to local SQLite fallback.")
        fallback_db = FallbackSessionLocal()
        try:
            yield fallback_db
        finally:
            fallback_db.close()
    finally:
        try:
            db.close()
        except:
            pass
