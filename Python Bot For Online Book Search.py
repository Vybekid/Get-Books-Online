import requests
import json

# --- Configuration ---
# Replace 'YOUR_API_KEY' with your actual Google Books API key if you have one.
# If you don't have one, you can try leaving it as an empty string,
# but you might hit rate limits or restrictions quickly.
API_KEY = "AIzaSyB5nE3v0qO7JQAXd2mqyAxpIrATNXVE8DA"  #  <--- PUT YOUR API KEY HERE if you have one

# Google Books API endpoint
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def search_books(query, max_results=5):
    """
    Searches for books using the Google Books API.

    Args:
        query (str): The search term (e.g., book title, author, ISBN).
        max_results (int): Maximum number of results to return.

    Returns:
        list: A list of dictionaries, where each dictionary contains book info,
              or None if an error occurs or no books are found.
    """
    params = {
        'q': query,
        'maxResults': max_results
    }
    if API_KEY:
        params['key'] = API_KEY

    try:
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        data = response.json()

        if 'items' in data:
            books_found = []
            for item in data['items']:
                book_info = {
                    'id': item.get('id'),
                    'title': item['volumeInfo'].get('title', 'N/A'),
                    'authors': ", ".join(item['volumeInfo'].get('authors', ['N/A'])),
                    'publisher': item['volumeInfo'].get('publisher', 'N/A'),
                    'published_date': item['volumeInfo'].get('publishedDate', 'N/A'),
                    'description': item['volumeInfo'].get('description', 'N/A'),
                    'page_count': item['volumeInfo'].get('pageCount', 'N/A'),
                    'categories': ", ".join(item['volumeInfo'].get('categories', [])),
                    'thumbnail_link': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', 'N/A'),
                    'info_link': item['volumeInfo'].get('infoLink', 'N/A')
                }
                # Extract ISBNs
                isbns = {}
                for identifier in item['volumeInfo'].get('industryIdentifiers', []):
                    if identifier['type'] == 'ISBN_10':
                        isbns['isbn10'] = identifier['identifier']
                    elif identifier['type'] == 'ISBN_13':
                        isbns['isbn13'] = identifier['identifier']
                book_info.update(isbns)

                books_found.append(book_info)
            return books_found
        else:
            print("No books found for your query.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Google Books API: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding API response.")
        return None
    except KeyError as e:
        print(f"Unexpected API response format (missing key: {e}). Please check the API documentation.")
        print("Raw response content:", response.text) # Helpful for debugging
        return None


def display_book_info(book):
    """Prints formatted book information."""
    print("-" * 40)
    print(f"Title: {book.get('title')}")
    print(f"Authors: {book.get('authors')}")
    if book.get('isbn13'):
        print(f"ISBN-13: {book.get('isbn13')}")
    if book.get('isbn10'):
        print(f"ISBN-10: {book.get('isbn10')}")
    print(f"Publisher: {book.get('publisher')}")
    print(f"Published Date: {book.get('published_date')}")
    print(f"Page Count: {book.get('page_count')}")
    print(f"Categories: {book.get('categories')}")
    # Truncate description for brevity
    description = book.get('description', 'N/A')
    if description and len(description) > 150:
        description = description[:150] + "..."
    print(f"Description: {description}")
    print(f"Thumbnail: {book.get('thumbnail_link')}")
    print(f"More Info: {book.get('info_link')}")
    print("-" * 40)

if __name__ == "__main__":
    search_query = input("Enter book title, author, or ISBN to search: ")
    if not search_query.strip():
        print("Search query cannot be empty.")
    else:
        print(f"\nSearching for '{search_query}'...\n")
        books = search_books(search_query, max_results=3) # Fetch top 3 results

        if books:
            if not books: # Empty list returned by search_books means "No books found" message was already printed
                pass
            else:
                print(f"Found {len(books)} book(s):\n")
                for book_data in books:
                    display_book_info(book_data)
        elif books is None: # Indicates an error occurred during search
            print("Book search failed due to an error.")