from fastapi import FastAPI
from mangum import Mangum
from backend.routers import auth, operations, upload, graph, dashboard, geolocation, messages, telefones, ips, intelligence, dashboard_extended

app = FastAPI(title="Forense API", root_path="/api")

# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(operations.router, prefix="/operations", tags=["operations"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(geolocation.router, prefix="/geolocation", tags=["geolocation"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(telefones.router, prefix="/telefones", tags=["telefones"])
app.include_router(ips.router, prefix="/ips", tags=["ips"])
app.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
app.include_router(dashboard_extended.router, prefix="/dashboard-extended", tags=["dashboard-extended"])

@app.get("/")
def read_root():
    return {"message":"Forense API Running"}

# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
