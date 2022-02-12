# Goodreads Scraper

This script scrapes reviews from a Goodreads user. It populates a MD file for Hugo, requiring shortcode templates called `booktile` and `oldbooktile`, to populate currently reading and read books respectively. Those shortcodes can be found [here](https://github.com/beccalunch/beccalynch/tree/main/themes/researcher/layouts/shortcodes).

To run:
```
python goodreads.py --user_id <goodreads-user-id> --out_markdown /path/to/book/markdown.md
```