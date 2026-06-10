from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import time

app = FastAPI(
    title="Product Review Processor",
    description="GitOps-deployed microservice for processing product reviews",
    version="1.0.0"
)

POSITIVE_WORDS = ["brilliant", "excellent", "perfect", "great", "good", "happy", "comfortable"]
NEGATIVE_WORDS = ["terrible", "poor", "disappointed", "waste", "broken", "awful", "died"]

# Simple in-memory metrics
metrics = {
    "requests_total": 0,
    "positive_reviews_total": 0,
    "negative_reviews_total": 0,
    "neutral_reviews_total": 0,
    "processing_seconds_total": 0.0
}

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

@app.get("/metrics")
def prometheus_metrics():
    output = []
    output.append("# HELP requests_total Total number of review analysis requests")
    output.append("# TYPE requests_total counter")
    output.append(f"requests_total {metrics['requests_total']}")
    output.append("# HELP positive_reviews_total Total positive reviews")
    output.append("# TYPE positive_reviews_total counter")
    output.append(f"positive_reviews_total {metrics['positive_reviews_total']}")
    output.append("# HELP negative_reviews_total Total negative reviews")
    output.append("# TYPE negative_reviews_total counter")
    output.append(f"negative_reviews_total {metrics['negative_reviews_total']}")
    output.append("# HELP neutral_reviews_total Total neutral reviews")
    output.append("# TYPE neutral_reviews_total counter")
    output.append(f"neutral_reviews_total {metrics['neutral_reviews_total']}")
    output.append("# HELP processing_seconds_total Total seconds spent processing")
    output.append("# TYPE processing_seconds_total counter")
    output.append(f"processing_seconds_total {metrics['processing_seconds_total']:.4f}")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(output))

@app.post("/analyse", response_model=ReviewResult)
def analyse_review(review: Review):
    start = time.time()
    sentiment, score, keywords = analyse_sentiment(review.review_text)
    elapsed = time.time() - start
    metrics["requests_total"] += 1
    metrics["processing_seconds_total"] += elapsed
    if sentiment == "positive":
        metrics["positive_reviews_total"] += 1
    elif sentiment == "negative":
        metrics["negative_reviews_total"] += 1
    else:
        metrics["neutral_reviews_total"] += 1
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
