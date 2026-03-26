import os, json

def read_fhir_dataset(dataset_path, max_files=None):
    bundles = []
    count = 0

    for root, _, files in os.walk(dataset_path):
        for file in files:
            if file.endswith(".json"):
                try:
                    with open(os.path.join(root, file)) as f:
                        data = json.load(f)
                        bundles.append(data)
                        count += 1

                    if max_files and count >= max_files:
                        print(f"🛑 File limit reached: {max_files}")
                        return bundles

                except Exception:
                    pass

    return bundles
