import logging
import os
from logging.handlers import RotatingFileHandler
import yaml


def configure_logger(name: str, project_root: str):
    """Configure and return a logger that writes to `worker.log` in the project root.

    Reads `log_level` from project `config.yaml` if available. Safe-fails to INFO.
    """
    log_file = os.path.join(project_root, "worker.log")
    logger = logging.getLogger(name)
    level = logging.INFO
    config_path = os.path.join(project_root, "config.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
                level_name = cfg.get('log_level') or (cfg.get('logging') or {}).get('level')
                if level_name:
                    level = getattr(logging, str(level_name).upper(), logging.INFO)
        except Exception:
            # keep default level
            pass

    logger.setLevel(level)

    if not logger.handlers:
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'))
        logger.addHandler(file_handler)

        console = logging.StreamHandler()
        console.setLevel(logging.ERROR)
        console.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(console)

    return logger
