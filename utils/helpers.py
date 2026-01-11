from bson.objectid import ObjectId
from datetime import datetime

def to_jsonable(doc, exclude=None):
    if not doc:
        return None
    exclude = exclude or []
    out = {}
    for k, v in doc.items():
        if k in exclude:
            continue
        if k == "_id":
            out["id"] = str(v)
        elif isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat() + "Z"
        else:
            out[k] = v
    return out
