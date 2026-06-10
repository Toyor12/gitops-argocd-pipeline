from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(
    title="Product Review Processor",
    description="GitOps-deployed microservice for processing product reviews",
    version="1.0.0"
)

POSITIVE_WORDS = ["brilliant", "excellent", "perfect", "great", "good", "happy", "comfortable"]
NEGATIVE_WORDS = ["terrible", "poor", "disappointed", "waste", "broken", "awful", "died"]

class Review(BaseModel):
    review_id: int
    product_name: str
    review_text: str
    rating: Optional[int] = None

class ReviewResult(BaseModel):
    review_id: int
    product_name: str
    sentiment: str
    sentiment_score: float
    keywords: list[str]

def analyse_sentiment(text: str) -> tuple[str, float, list[str]]:
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    total = pos + neg
    score = round((pos - neg) / total, 2) if total > 0 else 0.0
    sentiment = "positive" if pos > neg else "negative" if neg > pos else "neutral"
    keywords = [w for w in POSITIVE_WORDS + NEGATIVE_WORDS if w in text_lower]
    return sentiment, score, keywords

@app.get("/health")
def health():
    return {"status": "healthy", "service": "product-review-processor"}

@app.post("/analyse", response_model=ReviewResult)
def analyse_review(review: Review):
    sentiment, score, keywords = analyse_sentiment(review.review_text)
    return ReviewResult(
        review_id=review.review_id,
        product_name=review.product_name,
        sentiment=sentiment,
        sentiment_score=score,
        keywords=keywords
    )

@app.get("/")
def root():
    return {"message": "Product Review Processor — GitOps deployed via ArgoCD"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
