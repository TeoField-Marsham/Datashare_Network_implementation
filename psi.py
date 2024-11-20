# PSI

# TO DO:
# function to take a hash and define it under a group G python
# start working on the readme project report

import random
from hashlib import blake2b

# Simple paramaters used for demo purposes
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
    # Server's keyword set
    server_keywords = {'doc1': ['apple', 'banana', 'cherry', 'apple'],}

    # Hash/encrypt server's keywords
    server_elements = {doc_id: [hash_to_int(kwd) for kwd in keywords]
                        for doc_id, keywords in server_keywords.items()}

    return server_elements

def client_setup():
    # Client inputs the keywords they wish to search for
    user_input = input("Please enter keywords to search separated by spaces: ").strip()
    client_keywords = [word for word in user_input.split() if word]

    # Hash/encrypt client's keywords to integers
    client_elements = [hash_to_int(kwd) for kwd in client_keywords]

    return client_elements

def perform_psi(client_elements, server_elements):

    # Client generates a secret and exponentiates their hashed elements
    client_secret = generate_secret()
    client_transformed_elements = [pow(G, elem * client_secret, P) for elem in client_elements]

    """Client sends client_transformed_elements to server"""

    counts = []
    for doc_id, server_element in server_elements.items():

        # Server generates a secret and exponentiates their hashed elements
        server_secret = generate_secret()
        server_transformed_elements = [pow(G, elem * server_secret, P) for elem in server_element]

        # Server exponentiates client's elements with server's secret
        client_elements_server = [pow(elem, server_secret, P) for elem in client_transformed_elements]

        """Server sends server_transformed_elements and client_elements_server to client"""

        # Client exponentiates server's transformed elements with client_secret
        server_elements_client = [pow(elem, client_secret, P) for elem in server_transformed_elements]

        # Client computes the intersection
        set_client = set(client_elements_server)
        set_server = set(server_elements_client)
        intersection = set_client.intersection(set_server)
        count = len(intersection)
        counts.append((doc_id, count))

    return counts


if __name__ == "__main__":

    server_elements = server_setup()
    client_elements = client_setup()

    # Perform PSI
    counts = perform_psi(client_elements, server_elements)

    for doc_id, count in counts:
        print(f"Document '{doc_id}' has {count} matching keyword(s).")