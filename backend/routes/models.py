from fastapi import APIRouter, HTTPException
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.utils.model_manager import ModelManager

router = APIRouter()
model_manager = ModelManager()

@router.get("/status")
async def get_model_status():
    """
    Get status of all loaded models.
    """
    try:
        status = model_manager.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_model(dataset_path: str):
    """
    Train a new ATS model with provided dataset.
    """
    try:
        # Implementation for training
        result = {"message": "Model training started", "status": "in_progress"}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_model_performance():
    """
    Get performance metrics of current models.
    """
    try:
        metrics = model_manager.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_models():
    """
    Reload all models from disk.
    """
    try:
        model_manager.reload_models()
        return {"message": "Models reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
