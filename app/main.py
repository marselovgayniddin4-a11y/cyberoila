from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app import models

app = FastAPI()

Base.metadata.create_all(bind=engine)


# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "CyberOila API ishlayapti"}


@app.post("/report")
def report(target: str, risk: str = "unknown", db: Session = Depends(get_db)):
    new_report = models.Report(target=target, risk=risk)
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "message": "Report qo‘shildi",
        "id": new_report.id,
        "target": target
    }


@app.get("/check/{target}")
def check(target: str, db: Session = Depends(get_db)):
    reports = db.query(models.Report).filter(models.Report.target == target).all()

    return {
        "target": target,
        "reports_count": len(reports),
        "risk": "high" if len(reports) > 0 else "low"
    }
