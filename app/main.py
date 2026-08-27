from fastapi import FastAPI
app = FastAPI(
    title= "BUG TRACKER V1",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message" :" bug tracking app is running"
    }
@app.get("/health")
def health_check():
    return {
        "status" : "healthy"
    }