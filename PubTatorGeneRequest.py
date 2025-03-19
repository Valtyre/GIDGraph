import requests


def get_gene(name: str) -> dict: 
    # Define the API endpoint and parameters
    url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
    params = {
        "query": name,
        "concept": "GENE",
        "format": "json",
        "limit": "1"
    }

    # Send the GET request
    response = requests.get(url, params=params)
    print(response)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        if data:  # Ensure data is not empty
            return data
        else:
            return {}
    else:
        print(f"Error: {response.status_code}")


if __name__ == '__main__':
    res = get_gene("GATA46")

    print(res)

