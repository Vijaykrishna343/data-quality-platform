import urllib.request, json, threading

def train(id):
    req = urllib.request.Request('http://127.0.0.1:8000/ml/train/22', 
        data=json.dumps({'target_column': 'Company', 'task_type': 'classification'}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        res = urllib.request.urlopen(req, timeout=45)
        data = json.loads(res.read().decode())
        print(f"Thread {id}: SUCCESS, Status: {data.get('status')}")
    except Exception as e:
        print(f"Thread {id}: FAILED:", str(e))

threads = [threading.Thread(target=train, args=(i,)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print("Concurrency test complete")
