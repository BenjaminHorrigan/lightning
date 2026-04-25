"""
Cryptographically-signed audit logging for AEGIS decisions.
Every classification decision is logged with integrity guarantees.
"""
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from lightning.models import ClassificationResult, TechnicalArtifact


class AuditLogger:
    """
    Maintains immutable audit log of all AEGIS classification decisions.

    Each log entry is cryptographically signed for integrity verification.
    """

    def __init__(self, log_path: str = "aegis_audit.jsonl", secret_key: Optional[str] = None):
        self.log_path = Path(log_path)
        self.secret_key = secret_key or self._generate_secret()

        # Ensure log file exists
        if not self.log_path.exists():
            self.log_path.touch()

    def log_decision(
        self,
        artifact: TechnicalArtifact,
        result: ClassificationResult,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a classification decision with cryptographic integrity.

        Returns:
            Unique audit ID for this decision.
        """
        audit_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Create content hash of input artifact
        artifact_hash = self._hash_artifact(artifact)

        # Create content hash of classification result
        result_hash = self._hash_result(result)

        # Build audit record
        audit_record = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "artifact_hash": artifact_hash,
            "result_hash": result_hash,
            "decision": result.decision.value,
            "classification": result.proof_tree.top_level_classification,
            "controlled_elements": result.proof_tree.controlled_elements,
            "regimes_checked": [r.value for r in result.regimes_checked],
            "confidence": result.confidence,
            "proof_steps_count": len(result.proof_tree.steps),
            "gaps_count": len(result.proof_tree.gaps),
            "citation_count": len(result.primary_citations),
            "context": context or {}
        }

        # Generate cryptographic signature
        signature = self._sign_record(audit_record)
        audit_record["signature"] = signature

        # Append to log file (JSONL format)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(audit_record) + "\n")

        return audit_id

    def verify_decision(self, audit_id: str) -> Dict[str, Any]:
        """
        Verify integrity of a logged decision.

        Returns:
            Verification result with integrity status.
        """
        record = self._find_record(audit_id)
        if not record:
            return {"verified": False, "error": "Audit record not found"}

        # Extract signature and verify
        stored_signature = record.pop("signature")
        computed_signature = self._sign_record(record)

        if hmac.compare_digest(stored_signature, computed_signature):
            return {
                "verified": True,
                "audit_id": audit_id,
                "timestamp": record["timestamp"],
                "decision": record["decision"]
            }
        else:
            return {
                "verified": False,
                "error": "Cryptographic signature mismatch - record may be tampered"
            }

    def get_audit_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of audit log for the last N days."""
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        decisions = {"ALLOW": 0, "REFUSE": 0, "ESCALATE": 0}
        total_decisions = 0
        regimes_used = set()

        if not self.log_path.exists():
            return {
                "period_days": days,
                "total_decisions": 0,
                "decisions_breakdown": decisions,
                "regimes_used": [],
                "log_integrity": {"status": "no_log", "verified_records": 0, "total_records": 0}
            }

        with open(self.log_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line.strip())
                    record_time = datetime.fromisoformat(record["timestamp"].replace("Z", "")).timestamp()

                    if record_time >= cutoff_time:
                        decisions[record["decision"]] += 1
                        total_decisions += 1
                        regimes_used.update(record["regimes_checked"])
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return {
            "period_days": days,
            "total_decisions": total_decisions,
            "decisions_breakdown": decisions,
            "regimes_used": list(regimes_used),
            "log_integrity": self._check_log_integrity()
        }

    def export_audit_package(self, audit_id: str, output_dir: str) -> str:
        """
        Export complete audit package for regulatory submission.

        Includes original artifact, classification result, proof tree,
        and integrity verification.
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        record = self._find_record(audit_id)
        if not record:
            raise ValueError(f"Audit record {audit_id} not found")

        verification = self.verify_decision(audit_id)

        package = {
            "audit_record": record,
            "integrity_verification": verification,
            "export_timestamp": datetime.utcnow().isoformat() + "Z",
            "aegis_version": "0.1.0",  # TODO: get from package version
            "regulatory_note": "This audit package provides cryptographic proof of the classification decision and reasoning chain.",
            "verification_instructions": {
                "1": "Verify the integrity_verification.verified field is true",
                "2": "Check that audit_record.signature matches the record content",
                "3": "Validate timestamp is within expected processing window",
                "4": "Review proof_tree for complete reasoning chain",
                "5": "Cross-reference citations against official regulatory sources"
            }
        }

        package_file = output_path / f"aegis_audit_{audit_id[:8]}.json"
        with open(package_file, "w") as f:
            json.dump(package, f, indent=2)

        return str(package_file)

    def search_decisions(
        self,
        decision_type: Optional[str] = None,
        regime: Optional[str] = None,
        element: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search audit log with filters."""
        results = []

        if not self.log_path.exists():
            return results

        with open(self.log_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line.strip())

                    # Apply filters
                    if decision_type and record["decision"] != decision_type:
                        continue
                    if regime and regime not in record["regimes_checked"]:
                        continue
                    if element and element not in record["controlled_elements"]:
                        continue

                    # Date filters
                    record_date = record["timestamp"][:10]  # YYYY-MM-DD
                    if start_date and record_date < start_date:
                        continue
                    if end_date and record_date > end_date:
                        continue

                    results.append(record)

                except (json.JSONDecodeError, KeyError):
                    continue

        return results

    def _hash_artifact(self, artifact: TechnicalArtifact) -> str:
        """Create deterministic hash of artifact content."""
        # Use model_dump to get deterministic serialization
        content = artifact.model_dump_json(sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _hash_result(self, result: ClassificationResult) -> str:
        """Create deterministic hash of classification result."""
        # Hash key decision components, not the full result (which contains hashes)
        key_data = {
            "decision": result.decision.value,
            "controlled_elements": sorted(result.proof_tree.controlled_elements),
            "classification": result.proof_tree.top_level_classification,
            "proof_steps": [
                {"rule": s.rule_name, "conclusion": s.conclusion}
                for s in result.proof_tree.steps
            ]
        }
        content = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _sign_record(self, record: Dict[str, Any]) -> str:
        """Generate HMAC signature for audit record."""
        # Remove signature field if present
        record_copy = {k: v for k, v in record.items() if k != "signature"}
        content = json.dumps(record_copy, sort_keys=True)
        return hmac.new(
            self.secret_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()

    def _find_record(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """Find audit record by ID."""
        if not self.log_path.exists():
            return None

        with open(self.log_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line.strip())
                    if record.get("audit_id") == audit_id:
                        return record
                except json.JSONDecodeError:
                    continue
        return None

    def _check_log_integrity(self) -> Dict[str, Any]:
        """Check integrity of entire audit log."""
        if not self.log_path.exists():
            return {"status": "no_log", "verified_records": 0, "total_records": 0}

        total_records = 0
        verified_records = 0

        with open(self.log_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                total_records += 1
                try:
                    record = json.loads(line.strip())
                    stored_signature = record.pop("signature", "")
                    computed_signature = self._sign_record(record)

                    if hmac.compare_digest(stored_signature, computed_signature):
                        verified_records += 1
                except (json.JSONDecodeError, KeyError):
                    pass  # Count as unverified

        return {
            "status": "verified" if verified_records == total_records else "compromised",
            "verified_records": verified_records,
            "total_records": total_records,
            "integrity_percentage": (verified_records / total_records * 100) if total_records > 0 else 0
        }

    def _generate_secret(self) -> str:
        """Generate random secret key for new audit log."""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger