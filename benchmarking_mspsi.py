# SPEED TEST FOR MSPSI

import time
import mspsi

def client_setup_override():
    # Enter test keywords
    client_keywords = ['apple', 'banana']

    # Assign IDs to the keywords
    client_keyword_ids = list(range(1, len(client_keywords)+1))

    # Hash/encrypt client's keywords to integers and map them to IDs
    client_elements = []
    client_element_id_map = {}
    for idx, kwd in zip(client_keyword_ids, client_keywords):
        elem = mspsi.hash_to_int(kwd)
        client_elements.append(elem)
        if elem not in client_element_id_map:
            client_element_id_map[elem] = []
        client_element_id_map[elem].append(idx)

    return client_elements, client_element_id_map

# Override the client_setup function in psi.py
mspsi.client_setup = client_setup_override
server_elements_per_doc = mspsi.server_setup()
client_elements, client_element_id_map = mspsi.client_setup()

# Measure the time taken by perform_psi()
start_time = time.time()
counts_per_doc = mspsi.perform_ms_psi(client_elements, server_elements_per_doc, client_element_id_map)
end_time = time.time()
elapsed_time = end_time - start_time

for doc_id, ids in counts_per_doc:
    ids = sorted(ids)
    if ids:
        ids_str = ', '.join(map(str, ids))
        print(f"Document '{doc_id}' has matching keyword IDs: {ids_str}.")
    else:
        print(f"Document '{doc_id}' has no matching keywords.")

elapsed_time_ms = elapsed_time * 1000
print(f"Time taken by perform_ms_psi(): {elapsed_time_ms:.5f} milliseconds")