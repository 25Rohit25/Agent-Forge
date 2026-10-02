import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def search_logs(
    service: str,
    time_range: Optional[str] = "1h",
    level: Optional[str] = None,
    keyword: Optional[str] = None,
    max_lines: int = 50
) -> Dict[str, Any]:
    """
    Search application logs for a given service.
    Filters by log level (INFO, WARN, ERROR, FATAL) or keyword query.
    """
    logs_dir = settings.LOGS_DIR
    if not logs_dir.exists():
        return {
            "error": "Logs directory not found",
            "matches_count": 0,
            "logs": []
        }

    # Normalize service name to find log file
    clean_service = service.strip().lower().replace("_", "-")
    target_file = logs_dir / f"{clean_service}.log"

    if not target_file.exists():
        # Try finding partial match
        matched_file = None
        for file in logs_dir.glob("*.log"):
            if clean_service in file.stem.lower() or file.stem.lower() in clean_service:
                matched_file = file
                break
        if matched_file:
            target_file = matched_file
        else:
            available = [f.stem for f in logs_dir.glob("*.log")]
            return {
                "error": f"Log file for service '{service}' not found.",
                "available_logs": available,
                "matches_count": 0,
                "logs": []
            }

    try:
        with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = [line.strip() for line in f if line.strip()]

        matched_lines: List[str] = []
        filter_level = level.upper() if level else None
        filter_keyword = keyword.lower() if keyword else None

        level_counts = {"INFO": 0, "WARN": 0, "ERROR": 0, "FATAL": 0}

        for line in all_lines:
            # Count levels in file
            for lvl in level_counts.keys():
                if f"[{lvl}]" in line or f" {lvl} " in line:
                    level_counts[lvl] += 1

            # Apply level filter
            if filter_level:
                if f"[{filter_level}]" not in line and f" {filter_level} " not in line:
                    continue

            # Apply keyword filter
            if filter_keyword:
                if filter_keyword not in line.lower():
                    continue

            matched_lines.append(line)

        # Slice to max_lines
        sliced_matches = matched_lines[:max_lines]

        return {
            "service": clean_service,
            "log_file": target_file.name,
            "time_range": time_range,
            "level_filter": level,
            "keyword_filter": keyword,
            "total_lines_scanned": len(all_lines),
            "matches_count": len(matched_lines),
            "level_distribution": level_counts,
            "logs": sliced_matches
        }
    except Exception as e:
        logger.error(f"Error reading logs for {service}: {e}")
        return {"error": str(e), "matches_count": 0, "logs": []}
