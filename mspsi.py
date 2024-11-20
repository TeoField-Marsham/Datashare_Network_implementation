# MS-PSI

# TO DO:
# start working on the readme project report

import random
from hashlib import blake2b
from collections import Counter

# Simple parameters used for demo purposes
P = 1019  # Large prime number for modulo operations
G = 2     # Primitive root modulo

def hash_to_int(kwd):
    # Hash a keyword to an integer
    hash_value = blake2b(kwd.encode(), digest_size=64).digest()
    return int.from_bytes(hash_value, 'big')

def generate_secret():
    # Generate a random secret exponent
    return random.randint(1, P - 2)

def server_setup():
    # Server's keyword sets
    server_documents = {
        'doc1': ['apple', 'banana', 'cherry', 'apple'],
        'doc2': ['banana', 'date', 'fig', 'banana'],
        'doc3': ['cherry', 'date', 'grape', 'date'],
        'doc4': ['apple', 'date', 'kiwi', 'date'],
        'doc5': ['banana', 'cherry', 'lemon', 'banana', 'cherry']
    }

    # Hash/encrypt server's keywords per document
    server_elements_per_doc = {doc_id: [hash_to_int(kwd) for kwd in keywords]
                                for doc_id, keywords in server_documents.items()}

    return server_elements_per_doc

def client_setup():
    # Client inputs the keywords they wish to search for
    user_input = input("Please enter keywords to search separated by spaces: ").strip()
    client_keywords = [word for word in user_input.split() if word]

    # Assign IDs to the keywords
    client_keyword_ids = list(range(1, len(client_keywords)+1))

    # Hash/encrypt client's keywords to integers and map them to IDs
    client_elements = []
    client_element_id_map = {}
    for idx, kwd in zip(client_keyword_ids, client_keywords):
        elem = hash_to_int(kwd)
        client_elements.append(elem)
        if elem not in client_element_id_map:
            client_element_id_map[elem] = []
        client_element_id_map[elem].append(idx)

    return client_elements, client_element_id_map

def perform_ms_psi(client_elements, server_elements_per_doc, client_element_id_map):

    # Client generates a secret and exponentiates their hashed elements
    client_secret = generate_secret()
    client_element_counts = Counter(client_elements)
    client_transformed_elements = {}
    for elem, count in client_element_counts.items():
        transformed_elem = pow(G, elem * client_secret, P)
        client_transformed_elements[transformed_elem] = {'count': count, 'ids': client_element_id_map[elem]}

    """Client sends client_transformed_elements to server"""

    counts_per_doc = []
    for doc_id, server_elements in server_elements_per_doc.items():

        # Server generates a secret and exponentiates their hashed elements
        server_secret = generate_secret()
        server_element_counts = Counter(server_elements)
        server_transformed_counts = {}
        for elem, count in server_element_counts.items():
            transformed_elem = pow(G, elem * server_secret, P)
            server_transformed_counts[transformed_elem] = count

        # Server exponentiates client's elements with server's secret
        client_elements_server = {}
        for transformed_elem, value in client_transformed_elements.items():
            transformed_elem_server = pow(transformed_elem, server_secret, P)
            client_elements_server[transformed_elem_server] = value  # value includes 'count' and 'ids'

        """Server sends server_transformed_elements and client_elements_server to client"""

        # Client exponentiates server's transformed elements with their secret
        server_elements_client = {}
        for elem, count in server_transformed_counts.items():
            transformed_elem = pow(elem, client_secret, P)
            server_elements_client[transformed_elem] = count

        # Client finds multiset intersection (considering multiplicities)
        intersection_ids = set()
        for elem in client_elements_server:
            if elem in server_elements_client:
                # Get the IDs from client_elements_server[elem]['ids']
                ids = client_elements_server[elem]['ids']
                intersection_ids.update(ids)
        counts_per_doc.append((doc_id, intersection_ids))

    return counts_per_doc


if __name__ == "__main__":

    server_elements_per_doc = server_setup()
    client_elements, client_element_id_map = client_setup()

    # Perform MS-PSI
    counts_per_doc = perform_ms_psi(client_elements, server_elements_per_doc, client_element_id_map)

    for doc_id, ids in counts_per_doc:
        ids = sorted(ids)
        if ids:
            ids_str = ', '.join(map(str, ids))
            print(f"Document '{doc_id}' has matching keyword IDs: {ids_str}.")
        else:
            print(f"Document '{doc_id}' has no matching keywords.")