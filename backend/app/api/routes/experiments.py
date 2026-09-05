import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.errors import NotFoundError
from app.database import get_db
from app.models.experiment import Experiment, ExperimentMetric
from app.models.user import User
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentDetailOut,
    ExperimentOut,
    ExperimentUpdate,
    MetricCreate,
    MetricOut,
)

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


def _get_owned_experiment(db: Session, experiment_id: uuid.UUID, user: User) -> Experiment:
    experiment = db.get(Experiment, experiment_id)
    if experiment is None or experiment.owner_id != user.id:
        raise NotFoundError("EXPERIMENT_NOT_FOUND", "The requested experiment could not be found.")
    return experiment


@router.post("", response_model=ExperimentOut, status_code=201)
def create_experiment(
    payload: ExperimentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    experiment = Experiment(owner_id=current_user.id, **payload.model_dump())
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return ExperimentOut.model_validate(experiment)


@router.get("", response_model=list[ExperimentOut])
def list_experiments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    experiments = db.scalars(
        select(Experiment).where(Experiment.owner_id == current_user.id).order_by(Experiment.created_at.desc())
    ).all()
    return [ExperimentOut.model_validate(e) for e in experiments]


@router.get("/{experiment_id}", response_model=ExperimentDetailOut)
def get_experiment(experiment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    experiment = _get_owned_experiment(db, experiment_id, current_user)
    return ExperimentDetailOut.model_validate(experiment)


@router.put("/{experiment_id}", response_model=ExperimentOut)
def update_experiment(
    experiment_id: uuid.UUID,
    payload: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experiment = _get_owned_experiment(db, experiment_id, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(experiment, field, value)
    db.commit()
    db.refresh(experiment)
    return ExperimentOut.model_validate(experiment)


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(experiment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    experiment = _get_owned_experiment(db, experiment_id, current_user)
    db.delete(experiment)
    db.commit()
    return None


@router.post("/{experiment_id}/metrics", response_model=MetricOut, status_code=201)
def add_metric(
    experiment_id: uuid.UUID,
    payload: MetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_experiment(db, experiment_id, current_user)
    metric = ExperimentMetric(experiment_id=experiment_id, **payload.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return MetricOut.model_validate(metric)


@router.get("/{experiment_id}/metrics", response_model=list[MetricOut])
def list_metrics(experiment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_experiment(db, experiment_id, current_user)
    metrics = db.scalars(
        select(ExperimentMetric).where(ExperimentMetric.experiment_id == experiment_id).order_by(ExperimentMetric.created_at)
    ).all()
    return [MetricOut.model_validate(m) for m in metrics]
