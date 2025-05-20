from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/data")
def get_data():
    with open("example.png", "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    return {
        "texts": ["Here is your data!"],
        "images_base64": [encoded],
        # "image_url": "https://example.com/image.png"  # Optional
    }


# uvicorn main:app --reload
