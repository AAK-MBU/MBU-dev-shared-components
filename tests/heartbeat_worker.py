"""Worker to run heartbeat in subprocess"""
import sys
from mbu_dev_shared_components.database.connection import RPAConnection


def main():
    """Run log heartbeat"""

    db_env = sys.argv[1]
    stop = sys.argv[2]
    servicename = sys.argv[3]
    heartbeat_interval = int(float(sys.argv[4]))
    details = sys.argv[5]

    with RPAConnection(db_env=db_env, commit=True) as test_worker_conn:
        test_worker_conn.log_heartbeat(
            stop=stop,
            servicename=servicename,
            heartbeat_interval=heartbeat_interval,
            details=details
        )


if __name__ == "__main__":
    main()
