"""Session cleanup service for expired sessions"""
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_
from datetime import datetime, timedelta
import logging

from ..db.base import SessionLocal
from ..db.models import Session, LLMEvent
from ..config import settings

logger = logging.getLogger(__name__)


class SessionCleanupService:
    """Service to clean up expired sessions"""

    @staticmethod
    def cleanup_expired_sessions(dry_run: bool = False) -> dict:
        """
        Clean up sessions that have been inactive for longer than the TTL.

        Args:
            dry_run: If True, only report what would be deleted without actually deleting

        Returns:
            Dictionary with cleanup statistics
        """
        db = SessionLocal()
        try:
            # Calculate expiration cutoff time
            cutoff_time = datetime.utcnow() - timedelta(days=settings.session_ttl_days)

            logger.info(f"Starting session cleanup (dry_run={dry_run})")
            logger.info(f"Cutoff time: {cutoff_time}")

            # Query expired sessions
            expired_sessions = db.query(Session).filter(
                Session.last_activity < cutoff_time
            ).all()

            session_count = len(expired_sessions)
            logger.info(f"Found {session_count} expired sessions")

            if session_count == 0:
                return {
                    "success": True,
                    "dry_run": dry_run,
                    "sessions_deleted": 0,
                    "events_deleted": 0,
                    "message": "No expired sessions found"
                }

            # Count events that will be deleted
            session_ids = [session.id for session in expired_sessions]
            event_count = db.query(LLMEvent).filter(
                LLMEvent.session_id.in_(session_ids)
            ).count()

            logger.info(f"Found {event_count} events to delete")

            if dry_run:
                # Just report what would be deleted
                expired_session_ids = [session.session_id for session in expired_sessions]
                logger.info(f"DRY RUN: Would delete {session_count} sessions and {event_count} events")
                logger.info(f"Expired session IDs: {expired_session_ids[:10]}...")  # Show first 10

                return {
                    "success": True,
                    "dry_run": True,
                    "sessions_deleted": 0,
                    "events_deleted": 0,
                    "sessions_would_delete": session_count,
                    "events_would_delete": event_count,
                    "message": f"DRY RUN: Would delete {session_count} sessions and {event_count} events"
                }

            # Actually delete the sessions (cascade will delete events)
            deleted_session_count = 0
            for session in expired_sessions:
                logger.info(f"Deleting session: {session.session_id} (last active: {session.last_activity})")
                db.delete(session)
                deleted_session_count += 1

            db.commit()

            logger.info(f"Cleanup complete: Deleted {deleted_session_count} sessions and {event_count} events")

            return {
                "success": True,
                "dry_run": False,
                "sessions_deleted": deleted_session_count,
                "events_deleted": event_count,
                "message": f"Successfully deleted {deleted_session_count} sessions and {event_count} events"
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error during session cleanup: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Session cleanup failed: {str(e)}"
            }
        finally:
            db.close()

    @staticmethod
    def cleanup_inactive_sessions(inactive_hours: int = 24, dry_run: bool = False) -> dict:
        """
        Clean up sessions that have been inactive for a specified number of hours.
        This is a more aggressive cleanup for short-term inactive sessions.

        Args:
            inactive_hours: Number of hours of inactivity before deletion
            dry_run: If True, only report what would be deleted

        Returns:
            Dictionary with cleanup statistics
        """
        db = SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=inactive_hours)

            logger.info(f"Starting inactive session cleanup (inactive_hours={inactive_hours}, dry_run={dry_run})")
            logger.info(f"Cutoff time: {cutoff_time}")

            # Query inactive sessions
            inactive_sessions = db.query(Session).filter(
                and_(
                    Session.last_activity < cutoff_time,
                    Session.is_active == True
                )
            ).all()

            session_count = len(inactive_sessions)
            logger.info(f"Found {session_count} inactive sessions")

            if session_count == 0:
                return {
                    "success": True,
                    "dry_run": dry_run,
                    "sessions_marked_inactive": 0,
                    "message": "No inactive sessions found"
                }

            if dry_run:
                logger.info(f"DRY RUN: Would mark {session_count} sessions as inactive")
                return {
                    "success": True,
                    "dry_run": True,
                    "sessions_marked_inactive": 0,
                    "sessions_would_mark": session_count,
                    "message": f"DRY RUN: Would mark {session_count} sessions as inactive"
                }

            # Mark sessions as inactive (don't delete yet, just flag)
            marked_count = 0
            for session in inactive_sessions:
                session.is_active = False
                marked_count += 1

            db.commit()

            logger.info(f"Marked {marked_count} sessions as inactive")

            return {
                "success": True,
                "dry_run": False,
                "sessions_marked_inactive": marked_count,
                "message": f"Successfully marked {marked_count} sessions as inactive"
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error during inactive session cleanup: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Inactive session cleanup failed: {str(e)}"
            }
        finally:
            db.close()

    @staticmethod
    def get_cleanup_stats() -> dict:
        """
        Get statistics about sessions and potential cleanup targets.

        Returns:
            Dictionary with session statistics
        """
        db = SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=settings.session_ttl_days)

            # Total sessions
            total_sessions = db.query(Session).count()

            # Active sessions
            active_sessions = db.query(Session).filter(Session.is_active == True).count()

            # Expired sessions
            expired_sessions = db.query(Session).filter(
                Session.last_activity < cutoff_time
            ).count()

            # Inactive sessions (last 24 hours)
            inactive_cutoff = datetime.utcnow() - timedelta(hours=24)
            inactive_24h = db.query(Session).filter(
                and_(
                    Session.last_activity < inactive_cutoff,
                    Session.is_active == True
                )
            ).count()

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "inactive_sessions": total_sessions - active_sessions,
                "expired_sessions": expired_sessions,
                "inactive_24h": inactive_24h,
                "ttl_days": settings.session_ttl_days,
                "cutoff_time": cutoff_time.isoformat()
            }

        finally:
            db.close()


# Convenience function for cron jobs
def run_cleanup(dry_run: bool = False):
    """
    Run the cleanup job. Can be called from a cron job or scheduler.

    Args:
        dry_run: If True, only report what would be deleted
    """
    logger.info("Running scheduled session cleanup")
    result = SessionCleanupService.cleanup_expired_sessions(dry_run=dry_run)
    logger.info(f"Cleanup result: {result}")
    return result


if __name__ == "__main__":
    # Allow running as a standalone script for testing
    import sys

    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("Session Cleanup Utility")
    print("=" * 60)

    # Get stats first
    print("\nSession Statistics:")
    stats = SessionCleanupService.get_cleanup_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Run cleanup
    print(f"\nRunning cleanup (dry_run={dry_run})...")
    result = run_cleanup(dry_run=dry_run)
    print(f"\nResult: {result['message']}")

    if result.get('sessions_deleted', 0) > 0 or result.get('sessions_would_delete', 0) > 0:
        print(f"  Sessions deleted: {result.get('sessions_deleted', result.get('sessions_would_delete', 0))}")
        print(f"  Events deleted: {result.get('events_deleted', result.get('events_would_delete', 0))}")
