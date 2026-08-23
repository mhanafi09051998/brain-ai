import json, re
from official_runner import query_llm

prompt = "Generate a JSON tool call for function 'database_rollback' with parameters 'savepoint_id' (string 'sp_10') and 'force' (boolean true). Output ONLY valid JSON."
res = query_llm(prompt)
print("RAW RES:", repr(res))
m = re.search(r'\{.*\}', res, re.S)
if m:
    try:
        data = json.loads(m.group(0))
        print("PARSED:", data)
    except Exception as e:
        print("JSON ERR:", e)
else:
    print("NO MATCH")
