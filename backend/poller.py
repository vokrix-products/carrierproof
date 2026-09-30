import os
import time
import json
import datetime
import requests
import processor

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ["PRODUCT_ID"]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

REST_URL = f"{SUPABASE_URL}/rest/v1"
NOTIF_URL = "https://njyvnmczoydsaewvfhyq.supabase.co/rest/v1/notifications"

SB_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
}

def download_file(bucket, file_path):
    if file_path.startswith(bucket + "/"):
        file_path = file_path[len(bucket) + 1:]
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
        },
    )
    resp.raise_for_status()
    return resp.content

def upload_result(bucket, path, content_bytes, content_type="application/json"):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": content_type,
    }
    resp = requests.post(url, headers=headers, data=content_bytes)
    resp.raise_for_status()
    return url

def send_notification(customer_id, success):
    if success:
        payload = {
            "product_id": PRODUCT_ID,
            "customer_id": customer_id,
            "title": "Processing complete",
            "body": "Your upload has been processed successfully.",
            "type": "success",
            "read": False,
        }
    else:
        payload = {
            "product_id": PRODUCT_ID,
            "customer_id": customer_id,
            "title": "Processing failed",
            "body": "There was an error processing your upload.",
            "type": "error",
            "read": False,
        }
    try:
        requests.post(
            NOTIF_URL,
            headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
            json=payload,
        )
    except Exception as e:
        print("notification failed", e)

def update_job(job_id, status, output_file_path=None, result_summary=None):
    payload = {
        "status": status,
        "completed_at": datetime.datetime.utcnow().isoformat(),
    }
    if output_file_path:
        payload["output_file_path"] = output_file_path
    if result_summary:
        payload["result_summary"] = result_summary
    requests.patch(
        f"{REST_URL}/jobs?id=eq.{job_id}",
        headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        json=payload,
    )

def process_file(file_bytes):
    try:
        return processor.process_file(file_bytes)
    except TypeError:
        return processor.process_file(file_bytes, SUPABASE_URL, SUPABASE_SERVICE_KEY)

def poll():
    while True:
        try:
            query = "?status=eq.pending&job_type=eq.process_upload&product_id=eq." + PRODUCT_ID
            resp = requests.get(f"{REST_URL}/jobs{query}", headers=SB_HEADERS)
            resp.raise_for_status()
            jobs = resp.json()

            for job in jobs:
                job_id = job["id"]
                customer_id = job["customer_id"]
                input_file_path = job["input_file_path"]

                try:
                    file_bytes = download_file("uploads", input_file_path)
                    records = process_file(file_bytes)

                    for r in records:
                        requests.post(
                            f"{REST_URL}/records",
                            headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                            json={
                                "product_id": PRODUCT_ID,
                                "customer_id": customer_id,
                                "title": r["title"],
                                "status": r["status"],
                                "details": r["details"],
                                "source_file_path": job["input_file_path"],
                                "due_date": r.get("due_date"),
                            },
                        )

                    result = {"records": records}
                    result_bytes = json.dumps(result).encode("utf-8")
                    output_path = f"results/{job_id}/result.json"
                    upload_result("results", output_path, result_bytes)

                    update_job(
                        job_id,
                        "completed",
                        output_file_path=output_path,
                        result_summary=f"Processed {len(records)} records",
                    )
                    send_notification(customer_id, True)

                except Exception as e:
                    print("job failed", job_id, e)
                    update_job(job_id, "failed", result_summary=str(e))
                    send_notification(customer_id, False)

        except Exception as e:
            print("poll loop error", e)

        time.sleep(60)

if __name__ == "__main__":
    print("Poller started")
    poll()
