import json
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pathlib import Path
from .schemas import EvaluationResponse

class EvaluationStore(ABC):
    @abstractmethod
    def save(self, evaluation: EvaluationResponse) -> None:
        pass

    @abstractmethod
    def get(self, evaluation_id: str) -> Optional[EvaluationResponse]:
        pass

    @abstractmethod
    def list_all(self) -> List[EvaluationResponse]:
        pass

class FileEvaluationStore(EvaluationStore):
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _get_path(self, eval_id: str) -> Path:
        safe_id = "".join(c for c in eval_id if c.isalnum() or c in ('-', '_'))
        return self.directory / f"{safe_id}.json"

    def save(self, evaluation: EvaluationResponse) -> None:
        path = self._get_path(evaluation.evaluation_id)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(evaluation.model_dump_json(indent=2))

    def get(self, evaluation_id: str) -> Optional[EvaluationResponse]:
        path = self._get_path(evaluation_id)
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return EvaluationResponse(**data)

    def list_all(self) -> List[EvaluationResponse]:
        evals = []
        for file_path in self.directory.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    evals.append(EvaluationResponse(**data))
            except Exception:
                pass
        return sorted(evals, key=lambda e: e.created_at, reverse=True)
