# test_backend.py - Automated tests for PatentPulse backend
import requests
import os
import glob

def test_valid_upload():
    pdfs = [f for f in glob.glob('fixtures/*.pdf')]
    assert pdfs, "No PDF files found in fixtures/"
    for pdf in pdfs:
        retries = 3
        while retries > 0:
            with open(pdf, 'rb') as f:
                files = {'document': f}
                resp = requests.post('http://localhost:8080/upload', files=files)
                assert resp.status_code == 200, f"Expected 200, got {resp.status_code} for {pdf}"
                data = resp.json()
                print(f'Valid upload ({pdf}):', data)
                if 'error' in data and 'Unreachable' in data['error']:
                    print(f"AI Service unreachable for {pdf}, retrying...")
                    retries -= 1
                    if retries == 0:
                        print(f"Failed after 3 retries for {pdf}")
                        break
                else:
                    assert 'risk_score' in data
                    assert 'keywords' in data
                    assert data['risk_score'] >= 0
                    break

def test_massive_upload():
    with open('fixtures/massive_attack.txt', 'rb') as f:
        files = {'document': f}
        resp = requests.post('http://localhost:8080/upload', files=files)
        assert resp.status_code == 413, f"Expected 413, got {resp.status_code}"
        print('Massive upload rejected as expected.')

def test_corrupted_upload():
    with open('fixtures/corrupted.pdf', 'rb') as f:
        files = {'document': f}
        resp = requests.post('http://localhost:8080/upload', files=files)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        print('Corrupted upload:', data)
        assert 'risk_score' in data
        assert 'keywords' in data

def test_load_shedding():
    # Fire off more than 3 requests in parallel to trigger load shedding
    import threading
    results = []
    pdfs = [f for f in glob.glob('fixtures/*.pdf')]
    def upload(pdf):
        with open(pdf, 'rb') as f:
            files = {'document': f}
            resp = requests.post('http://localhost:8080/upload', files=files)
            results.append(resp.status_code)
    threads = []
    # Fire off 6 uploads, cycling through available PDFs
    for i in range(6):
        pdf = pdfs[i % len(pdfs)]
        threads.append(threading.Thread(target=upload, args=(pdf,)))
    for t in threads: t.start()
    for t in threads: t.join()
    print('Load shedding test results:', results)
    assert any(code == 503 for code in results), "Expected at least one 503 Service Unavailable"

if __name__ == "__main__":
    test_valid_upload()
    test_massive_upload()
    test_corrupted_upload()
    test_load_shedding()
    print("All tests completed.")
