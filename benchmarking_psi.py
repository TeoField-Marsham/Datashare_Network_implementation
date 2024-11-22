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

# Begin total timing
total_start_time = time.time()

server_elements = psi.server_setup()
client_elements = psi.client_setup()

# Measure the time taken by client_transform()
start_time = time.time()
client_secret, client_transformed_elements = psi.client_transform(client_elements)
end_time = time.time()
client_transform_time = end_time - start_time

"""Client sends client_transformed_elements to server"""

# Measure the time taken by server_process()
start_time = time.time()
server_data = psi.server_process(server_elements, client_transformed_elements)
end_time = time.time()
server_process_time = end_time - start_time

"""Server sends server_transformed_elements and client_elements_server to client"""

# Measure the time taken by client_compute_intersection()
start_time = time.time()
counts = psi.client_compute_intersection(client_secret, server_data)
end_time = time.time()
client_compute_intersection_time = end_time - start_time

# End total timing
total_end_time = time.time()
total_time = total_end_time - total_start_time

print("\n")
for doc_id, count in counts:
    print(f"Document '{doc_id}' has {count} matching keyword(s).")

print("\n")
print(f"Time taken by client_transform(): {client_transform_time * 1000:.5f} milliseconds")
print(f"Time taken by server_process(): {server_process_time * 1000:.5f} milliseconds")
print(f"Time taken by client_compute_intersection(): {client_compute_intersection_time * 1000:.5f} milliseconds")
print(f"Total time taken: {total_time * 1000:.5f} milliseconds")
print("\n")