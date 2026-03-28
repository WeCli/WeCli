"""
Cron job utilities for OpenClaw agents.
Provides functions to export, import, and manage cron jobs.
"""
import subprocess
import json
from typing import List, Dict, Optional, Tuple


def get_all_cron_jobs() -> Tuple[List[Dict], Optional[str]]:
    """
    Fetch all cron jobs from openclaw.
    
    Returns:
        Tuple of (jobs_list, error_message)
        - jobs_list: List of cron job dictionaries
        - error_message: None if successful, error string if failed
    """
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            return [], result.stderr.strip() or "Failed to list cron jobs"
        
        data = json.loads(result.stdout)
        jobs = data.get("jobs", [])
        
        # Extract and clean job data
        clean_jobs = []
        for job in jobs:
            schedule = job.get("schedule", {})
            schedule_kind = schedule.get("kind")  # "cron" | "at" | "every"
            
            clean_job = {
                "name": job.get("name"),
                "agentId": job.get("agentId"),
                "scheduleKind": schedule_kind,
                "cron": schedule.get("expr") if schedule_kind == "cron" else None,
                "tz": schedule.get("tz") if schedule_kind == "cron" else None,
                "at": schedule.get("at") if schedule_kind == "at" else None,
                "every": schedule.get("interval") if schedule_kind == "every" else None,
                "message": job.get("payload", {}).get("message"),
                "session": job.get("sessionTarget"),
                "mode": job.get("delivery", {}).get("mode"),
                "enabled": job.get("enabled", True),
                "deleteAfterRun": job.get("deleteAfterRun", False),
                "wakeMode": job.get("wakeMode", "now"),
            }
            clean_jobs.append(clean_job)
        
        return clean_jobs, None
        
    except subprocess.TimeoutExpired:
        return [], "Timeout while fetching cron jobs"
    except json.JSONDecodeError as e:
        return [], f"Failed to parse cron jobs JSON: {e}"
    except Exception as e:
        return [], str(e)


def get_agent_cron_jobs(agent_id: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Fetch cron jobs for a specific agent.
    
    Args:
        agent_id: The agent ID to filter by
        
    Returns:
        Tuple of (jobs_list, error_message)
    """
    all_jobs, error = get_all_cron_jobs()
    if error:
        return [], error
    
    # Filter jobs by agent ID
    agent_jobs = [job for job in all_jobs if job.get("agentId") == agent_id]
    return agent_jobs, None


def restore_cron_job(job: Dict, target_agent: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Restore a single cron job.
    
    Args:
        job: Job dictionary with fields from get_all_cron_jobs output.
             Supports scheduleKind: "cron", "at", "every".
        target_agent: Optional new agent name (if different from original)
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        agent_name = target_agent or job.get("agentId") or ""
        schedule_kind = job.get("scheduleKind", "cron")
        
        cmd = [
            "openclaw", "cron", "add",
            "--name", job.get("name") or "",
            "--agent", agent_name,
            "--session", job.get("session") or "isolated",
            "--message", job.get("message") or "",
            "--wake", job.get("wakeMode") or "now",
        ]
        
        # Schedule type specific flags
        if schedule_kind == "cron":
            cmd.extend(["--cron", job.get("cron") or ""])
            tz = job.get("tz")
            if tz:
                cmd.extend(["--tz", tz])
        elif schedule_kind == "at":
            cmd.extend(["--at", job.get("at") or ""])
        elif schedule_kind == "every":
            cmd.extend(["--every", job.get("every") or ""])
        else:
            return False, f"Unknown schedule kind: {schedule_kind}"
        
        # Optional flags
        if job.get("deleteAfterRun"):
            cmd.append("--delete-after-run")
        
        if not job.get("enabled", True):
            cmd.append("--disabled")
        
        # Handle delivery mode
        mode = job.get("mode")
        if mode == "announce":
            cmd.append("--announce")
        elif mode == "none" or mode is None:
            cmd.append("--no-deliver")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr.strip() or "Failed to add cron job"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout while adding cron job"
    except Exception as e:
        return False, str(e)


def restore_cron_jobs(jobs: List[Dict], target_agent: Optional[str] = None) -> Tuple[int, List[str]]:
    """
    Restore multiple cron jobs.
    
    Args:
        jobs: List of job dictionaries
        target_agent: Optional new agent name for all jobs
        
    Returns:
        Tuple of (success_count, error_messages)
    """
    success_count = 0
    errors = []
    
    for job in jobs:
        success, error = restore_cron_job(job, target_agent)
        if success:
            success_count += 1
        else:
            errors.append(f"{job.get('name', 'unknown')}: {error}")
    
    return success_count, errors


def export_cron_jobs_to_file(output_file: str = "cron_backup.json") -> Tuple[int, Optional[str]]:
    """
    Export all cron jobs to a JSON file.
    
    Args:
        output_file: Path to output JSON file
        
    Returns:
        Tuple of (job_count, error_message)
    """
    jobs, error = get_all_cron_jobs()
    if error:
        return 0, error
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        return len(jobs), None
    except Exception as e:
        return 0, str(e)


def import_cron_jobs_from_file(input_file: str = "cron_backup.json", target_agent: Optional[str] = None) -> Tuple[int, List[str]]:
    """
    Import cron jobs from a JSON file.
    
    Args:
        input_file: Path to input JSON file
        target_agent: Optional new agent name for all jobs
        
    Returns:
        Tuple of (success_count, error_messages)
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            jobs = json.load(f)
        
        return restore_cron_jobs(jobs, target_agent)
        
    except FileNotFoundError:
        return 0, [f"File not found: {input_file}"]
    except json.JSONDecodeError as e:
        return 0, [f"Invalid JSON: {e}"]
    except Exception as e:
        return 0, [str(e)]
