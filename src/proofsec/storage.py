import json
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pathlib import Path
from .schemas import CustomEvaluationRecord

class EvaluationStore(ABC):
    @abstractmethod
    def save(self, record: CustomEvaluationRecord) -> None:
        pass

    @abstractmethod
    def get(self, evaluation_id: str) -> Optional[CustomEvaluationRecord]:
        pass

    @abstractmethod
    def list_all(self) -> List[CustomEvaluationRecord]:
        pass

class FileEvaluationStore(EvaluationStore):
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _get_path(self, eval_id: str) -> Path:
        safe_id = "".join(c for c in eval_id if c.isalnum() or c in ('-', '_'))
        return self.directory / f"{safe_id}.json"

    def save(self, record: CustomEvaluationRecord) -> None:
        path = self._get_path(record.response.evaluation_id)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(record.model_dump_json(indent=2))

    def get(self, evaluation_id: str) -> Optional[CustomEvaluationRecord]:
        path = self._get_path(evaluation_id)
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return CustomEvaluationRecord(**data)

    def list_all(self) -> List[CustomEvaluationRecord]:
        evals = []
        for file_path in self.directory.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    evals.append(CustomEvaluationRecord(**data))
            except Exception:
                pass
        return sorted(evals, key=lambda r: r.response.created_at, reverse=True)
