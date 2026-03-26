from collections import defaultdict

def extract_patient_id(resource):
    ref = (
        resource.get("subject", {}).get("reference") or
        resource.get("patient", {}).get("reference")
    )
    if ref and "urn:uuid:" in ref:
        return ref.split("urn:uuid:")[-1]
    return None


def group_by_patient(bundles):
    patient_data = defaultdict(list)

    for bundle in bundles:
        if bundle.get("resourceType") == "Bundle":
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                pid = extract_patient_id(resource)
                if pid:
                    patient_data[pid].append(resource)

    return patient_data
