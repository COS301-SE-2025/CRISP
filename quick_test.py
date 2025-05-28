
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crisp_anonymization'))

# Direct imports
from enums import AnonymizationLevel, DataType
from context import AnonymizationContext

print("Testing CRISP Anonymization...")
context = AnonymizationContext()
result = context.execute_anonymization("192.168.1.1", DataType.IP_ADDRESS, AnonymizationLevel.MEDIUM)
print(f"Test result: 192.168.1.1 → {result}")
