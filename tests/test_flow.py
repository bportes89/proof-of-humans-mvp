import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    print("Testing Proof of Humans Flow...")
    
    # 1. Enroll
    print("\n[1] Starting Enrollment...")
    try:
        res = requests.post(f"{BASE_URL}/enroll", json={"user_id": "test_user"})
        res.raise_for_status()
        session_data = res.json()
        print(f"Enrollment Session Started: {session_data}")
        session_id = session_data["session_id"]
    except Exception as e:
        print(f"Failed to start enrollment: {e}")
        return

    # Poll for completion
    print("Polling for enrollment completion...")
    for i in range(30):
        try:
            res = requests.get(f"{BASE_URL}/status")
            status = res.json()
            print(f"Status: {status['state']}, RPM: {status['rpm']:.1f}, Quality: {status['signal_quality']:.2f}")
            
            if status["state"] == "COMPLETED":
                print("Enrollment Completed!")
                print("Proof:", status["proof"])
                break
            elif status["state"] == "FAILED":
                print("Enrollment Failed!")
                return
        except Exception as e:
            print(f"Polling error: {e}")
            
        time.sleep(1)
    else:
        print("Timeout waiting for enrollment.")
        return

    # 2. Verify
    print("\n[2] Starting Verification...")
    try:
        res = requests.post(f"{BASE_URL}/verify", json={"user_id": "test_user"})
        res.raise_for_status()
        session_data = res.json()
        print(f"Verification Session Started: {session_data}")
        verify_session_id = session_data["session_id"]
    except Exception as e:
        print(f"Failed to start verification: {e}")
        return

    # Poll for completion
    print("Polling for verification completion...")
    for i in range(30):
        try:
            res = requests.get(f"{BASE_URL}/status")
            status = res.json()
            print(f"Status: {status['state']}, RPM: {status['rpm']:.1f}, Quality: {status['signal_quality']:.2f}, Match: {status.get('proof', {}).get('identity_match')}")
            
            if status["state"] == "COMPLETED":
                print("Verification Completed!")
                print("Proof:", status["proof"])
                break
            elif status["state"] == "FAILED":
                print("Verification Failed!")
                return
        except Exception as e:
            print(f"Polling error: {e}")
            
        time.sleep(1)
    else:
        print("Timeout waiting for verification.")

if __name__ == "__main__":
    test_flow()
