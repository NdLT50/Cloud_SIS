import re
from src.core.schemas import ProvisioningResult

class HybridValidator:
    def __init__(self):
        # Patterns that indicate a blatant violation of minimum security standards
        self.blocklist_patterns = [
            r"0\.0\.0\.0/0",                    # Open CIDR
            r"\bALL\s+PRIVILEGES\b",            # Broad DB permissions
            r"\bGRANT\s+ALL\b",                 # Broad DB permissions
            r"permit\s+ip\s+any\s+any"          # Cisco open access
        ]

    def validate(self, result: ProvisioningResult) -> ProvisioningResult:
        """
        Performs deterministic checks on the LLM output.
        If a blocked pattern is found in the requested, approved permissions, or suggested config, 
        override the risk_level to 10 and adjust the action taken to BLOCKED.
        """
        combined_text = f"{result.requested_permissions} {result.approved_permissions} {result.suggested_config}".upper()
        
        violation_found = False
        for pattern in self.blocklist_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                violation_found = True
                break
                
        if violation_found:
            # Override LLM risk assessment with deterministic blocking
            result.risk_level = 10
            result.action_taken = "BLOCKED"
            result.reasoning = "[SYSTEM OVERRIDE] Blatant violation detected (e.g., 0.0.0.0/0 or ALL PRIVILEGES). Request strictly blocked."
            result.approved_permissions = "NONE"
            result.suggested_config = "# [BLOCKED] No configuration generated due to critical security violation."

        return result
