CATEGORY_WEIGHT = {
    "phishing": 5,
    "crypto_fraud": 5,
    "scam_shop": 4,
    "telegram_scam": 3,
    "fake_account": 2,
    "other": 1
}






from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import engine, Base, SessionLocal
from app import models

app = FastAPI(title="CyberOila API")

# DB create tables
Base.metadata.create_all(bind=engine)


# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------
# HOME
# ------------------------
@app.get("/")
def home():
    return {"message": "CyberOila API ishlayapti 🚀"}


# ------------------------
# CREATE REPORT
# ------------------------
@app.post("/report")
def report(
    target: str,
    risk: str = "unknown",
    report_type: str = "other",
    category: str = "other",
    description: str = "",
    db: Session = Depends(get_db)
):
    new_report = models.Report(
        target=target,
        risk=risk,
        report_type=report_type,
        category=category,
        description=description
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "message": "Report qo‘shildi",
        "id": new_report.id,
        "target": new_report.target,
        "category": new_report.category,
        "risk": new_report.risk
    }


# ------------------------
# CHECK TARGET
# ------------------------
CATEGORY_WEIGHT = {
    "phishing": 5,
    "crypto_fraud": 5,
    "scam_shop": 4,
    "telegram_scam": 3,
    "fake_account": 2,
    "other": 1
}


@app.get("/check/{target}")
def check(target: str, db: Session = Depends(get_db)):

    blocked = db.query(models.Blacklist).filter(
        models.Blacklist.target == target
    ).first()

    if blocked:
        return {
            "target": target,
            "status": "BLACKLISTED",
            "risk": "critical"
        }

    reports = db.query(models.Report).filter(
        models.Report.target == target
    ).all()

    score = 0

    for r in reports:
        score += CATEGORY_WEIGHT.get(r.category, 1)

    if score >= 15:
        risk = "critical"
    elif score >= 8:
        risk = "high"
    elif score >= 3:
        risk = "medium"
    else:
        risk = "low"

    return {
        "target": target,
        "reports_count": len(reports),
        "score": score,
        "risk": risk
    }











# ------------------------
# ALL REPORTS
# ------------------------
@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(models.Report).all()

    return [
        {
            "id": r.id,
            "target": r.target,
            "risk": r.risk,
            "category": r.category,
            "description": r.description,
            "created_at": str(r.created_at)
        }
        for r in reports
    ]


# ------------------------
# STATS
# ------------------------
@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    reports = db.query(models.Report).all()

    targets = set(r.target for r in reports)

    return {
        "total_reports": len(reports),
        "unique_targets": len(targets)
    }


# ------------------------
# TOP TARGETS
# ------------------------
@app.get("/top")
def top(db: Session = Depends(get_db)):
    results = (
        db.query(
            models.Report.target,
            func.count(models.Report.id).label("count")
        )
        .group_by(models.Report.target)
        .order_by(func.count(models.Report.id).desc())
        .limit(5)
        .all()
    )

    return [
        {
            "target": r.target,
            "reports": r.count
        }
        for r in results
    ]
# ------------------------
# BLACKLIST
# ------------------------
@app.post("/blacklist/{target}")
def add_blacklist(target: str, db: Session = Depends(get_db)):
    item = models.Blacklist(
        target=target,
        reason="manual"
    )

    db.add(item)
    db.commit()

    return {
        "message": "Blacklisted",
        "target": target
    }
