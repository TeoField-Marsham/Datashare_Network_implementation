# SPEED TEST FOR PSI

import time
import psi

def client_setup_override():
    # Enter test keywords
    client_keywords = ['apple', 'banana']

    client_elements = [psi.hash_to_int(kwd) for kwd in client_keywords]
    return client_elements

# Override the client_setup function in psi.py
psi.client_setup = client_setup_override
server_elements = psi.server_setup()
client_elements = psi.client_setup()

# Measure the time taken by perform_psi()
start_time = time.time()
counts = psi.perform_psi(client_elements, server_elements)
end_time = time.time()
elapsed_time = end_time - start_time

for doc_id, count in counts:
    print(f"Document '{doc_id}' has {count} matching keyword(s).")

elapsed_time_ms = elapsed_time * 1000
print(f"Time taken by perform_psi(): {elapsed_time_ms:.5f} milliseconds")
