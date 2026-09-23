import os
import json
import time
import urllib.request
import urllib.error

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

    # Hantera CORS Preflight (OPTIONS-anrop från webbläsaren)
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "GEMINI_API_KEY saknas i miljövariablerna."})
        }

    try:
        body = json.loads(event.get("body", "{}"))
        user_text = body.get("text", "")

        if not user_text:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Ingen text skickades med."})
            }

        prompt = (
            f"Du är en studieassistent. Skapa en kort sammanfattning och ett quiz baserat på följande text.\n"
            f"Svara ENBART i giltigt JSON-format med följande struktur:\n"
            f"{{\n"
            f'  "summary": "En kort sammanfattning av texten",\n'
            f'  "quiz": [\n'
            f'    {{\n'
            f'      "question": "Fråga 1?",\n'
            f'      "options": ["A", "B", "C", "D"],\n'
            f'      "answer": "Det korrekta svaret"\n'
            f'    }}\n'
            f'  ]\n'
            f"}}\n\n"
            f"Text:\n{user_text}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        # Lista på godkända modeller att prova i ordning vid överbelastning (503)
        candidate_models = [
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.6-flash"
        ]

        last_error = None

        for model_name in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            # Prova upp till 2 gånger per modell
            for attempt in range(2):
                try:
                    with urllib.request.urlopen(req) as response:
                        res_data = response.read().decode("utf-8")
                        res_json = json.loads(res_data)
                        generated_text = res_json["candidates"][0]["content"]["parts"][0]["text"]

                        return {
                            "statusCode": 200,
                            "headers": headers,
                            "body": generated_text
                        }
                except urllib.error.HTTPError as e:
                    last_error = e
                    if e.code == 503:
                        time.sleep(1)  # Kort paus innan nytt försök eller nästa modell
                        continue
                    else:
                        break  # Om felet inte är 503, avbryt försöken för denna modell

        # Om alla modeller misslyckades
        raise last_error

    except urllib.error.HTTPError as e:
        error_content = e.read().decode("utf-8")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": f"HTTP Error {e.code}: {e.reason}", "details": error_content})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }