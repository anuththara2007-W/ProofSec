from typing import Dict, Any, List

class KaggleResultParser:
    @staticmethod
    def parse(raw_data: List[Dict[str, Any]], benchmark_slug: str) -> List[Dict[str, Any]]:
        normalized_results = []
        for raw_item in raw_data:
            model_name = raw_item.get("model", raw_item.get("model_name", "unknown"))
            score = raw_item.get("score", raw_item.get("accuracy", 0.0))
            rank = raw_item.get("rank", 0)
            tasks = raw_item.get("tasks", raw_item.get("task_count", 0))
            
            metadata = {}
            for k, v in raw_item.items():
                if k not in ["model", "model_name", "score", "accuracy", "rank", "tasks", "task_count"]:
                    metadata[k] = v
                    
            normalized = {
                "source": "kaggle",
                "benchmark": benchmark_slug,
                "model": model_name,
                "score": float(score),
                "rank": int(rank),
                "tasks": int(tasks),
                "metadata": metadata
            }
            normalized_results.append(normalized)
            
        return normalized_results
