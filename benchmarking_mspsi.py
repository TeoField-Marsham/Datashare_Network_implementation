# SPEED TEST FOR MSPSI

import time
import mspsi

def client_setup_override():
    # Enter test keywords
    client_keywords = ['apple', 'apple', 'date', 'banana']

    client_elements = [mspsi.hash_to_int(kwd) for kwd in client_keywords]
    return client_elements

# Override the client_setup function in psi.py
mspsi.client_setup = client_setup_override
server_elements_per_doc = mspsi.server_setup()
client_elements = mspsi.client_setup()

# Measure the time taken by perform_psi()
start_time = time.time()
counts_per_doc = mspsi.perform_ms_psi(client_elements, server_elements_per_doc)
end_time = time.time()
elapsed_time = end_time - start_time

for doc_id, count in counts_per_doc:
    print(f"Document '{doc_id}' has {count} matching keyword(s).")

elapsed_time_ms = elapsed_time * 1000
print(f"Time taken by perform_psi(): {elapsed_time_ms:.5f} milliseconds")