"""
Example code / usages
"""

from tiktek import TikTek

# Create instance
t = TikTek()

# Get all the subjects
print(t.get_subjects())

# Get book data on all math books
print(t.get_books(subject="מתמטיקה"))

# Find the book ID for that book in that subject
book_id = t.get_book_id("חשמל ומגנטיות", "פיזיקה")

# Print the raw url to the solution
print(t.get_solution_url(book_id, 4, 4))

# Download the solution
t.download_solution("tiktek.jpg", book_id, 4, 4)
