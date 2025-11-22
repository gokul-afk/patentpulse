import os
import random

# Since this script is now INSIDE 'fixtures/', we generate files in the current dir
OUTPUT_DIR = "./fixtures" 

def create_valid_text():
    """Creates a clean, readable text file simulating a patent abstract."""
    content = """
    ABSTRACT
    A system and method for distributed consensus in a network of unreliable processors. 
    The system utilizes a leader-follower architecture where the leader coordinates 
    state updates across the cluster. In the event of a partition, a new leader 
    election protocol is triggered. This ensures high availability and consistency 
    specifically for time-series data ingestion pipelines.
    """
    with open(f"{OUTPUT_DIR}/valid_sample.txt", "w") as f:
        f.write(content.strip())
    print(f"✅ Created valid_sample.txt (Normal Data)")

def create_massive_file():
    """Creates a 50MB file to test the 10MB Load Shedding limit."""
    # Write 50MB of dummy data
    size_in_mb = 50
    with open(f"{OUTPUT_DIR}/massive_attack.txt", "wb") as f:
        f.write(b"0" * (size_in_mb * 1024 * 1024))
    print(f"⚠️  Created massive_attack.txt ({size_in_mb}MB - Should fail upload)")

def create_corrupted_pdf():
    """Creates a fake PDF that contains binary garbage to crash parsers."""
    # Start with a real PDF header so it 'looks' real to basic checks
    header = b"%PDF-1.5\n"
    garbage = os.urandom(1024 * 10) # 10KB of random chaos
    with open(f"{OUTPUT_DIR}/corrupted.pdf", "wb") as f:
        f.write(header + garbage)
    print(f"☣️  Created corrupted.pdf (Malicious Binary Content)")

def main():
    if OUTPUT_DIR != "." and not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print("--- Generating PatentPulse Test Fixtures ---")
    create_valid_text()
    create_massive_file()
    create_corrupted_pdf()
    print(f"\n📂 Fixtures generated! Commit these files to Git.")

if __name__ == "__main__":
    main()