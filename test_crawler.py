"""
Test script for the web crawler.
Run this to test the crawler locally without starting the API server.
"""

from crawling.crawler import WebCrawler
import json


def print_crawl_results(pages):
    """Pretty print crawl results."""
    print("\n" + "="*80)
    print("CRAWL RESULTS")
    print("="*80)
    print(f"\nTotal pages crawled: {len(pages)}\n")
    
    # Count successes and failures
    successful = [p for p in pages if p['error'] is None]
    failed = [p for p in pages if p['error'] is not None]
    
    print(f"✓ Successful: {len(successful)}")
    print(f"✗ Failed: {len(failed)}\n")
    
    # Print successful pages
    if successful:
        print("-" * 80)
        print("SUCCESSFUL PAGES:")
        print("-" * 80)
        for i, page in enumerate(successful, 1):
            print(f"\n{i}. {page['url']}")
            print(f"   Title: {page['title']}")
            print(f"   HTML Length: {len(page['html']) if page['html'] else 0} characters")
    
    # Print failed pages
    if failed:
        print("\n" + "-" * 80)
        print("FAILED PAGES:")
        print("-" * 80)
        for i, page in enumerate(failed, 1):
            print(f"\n{i}. {page['url']}")
            print(f"   Error: {page['error']}")
    
    # Print all URLs
    print("\n" + "-" * 80)
    print("ALL CRAWLED URLS:")
    print("-" * 80)
    for i, page in enumerate(pages, 1):
        status = "✓" if page['error'] is None else "✗"
        print(f"{i:2d}. {status} {page['url']}")
    
    print("\n" + "="*80)


def main():
    """Test the crawler with a sample URL."""
    
    # You can change this to test with different URLs
    BASE_URL = "https://react.dev/reference/react"
    MAX_DEPTH = 2
    MAX_PAGES = 10
    
    print(f"Starting crawl of {BASE_URL}")
    print(f"Configuration: max_depth={MAX_DEPTH}, max_pages={MAX_PAGES}, timeout=10s")
    print("-" * 80)
    
    # Create and run crawler
    crawler = WebCrawler(
        base_url=BASE_URL,
        max_depth=MAX_DEPTH,
        max_pages=MAX_PAGES,
        timeout=10
    )
    
    pages = crawler.crawl()
    
    # Print results
    print_crawl_results(pages)
    
    # Optionally save results to JSON
    output_file = "crawl_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
