from database import engine
print(f"Database URL: {engine.url}")
print(f"Database Dialect: {engine.dialect.name}")
