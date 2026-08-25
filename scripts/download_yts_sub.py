import urllib.request, re, zipfile, io, os

def get_yts_subtitles(imdb_id="tt1745960"):
    url = f"https://yts-subs.com/movie-imdb/{imdb_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print("Error fetching page:", e)
        return False

    # Find Indonesian subtitle link
    # Look for table row containing Indonesian
    matches = re.findall(r'<tr[^>]*>.*?Indonesian.*?href="(/subtitles/[^"]+)".*?</tr>', html, re.DOTALL | re.IGNORECASE)
    if not matches:
        # Fallback to general subtitle match
        matches = re.findall(r'href="(/subtitles/[^"]+)"', html)

    print(f"Found {len(matches)} subtitle matches")
    if not matches:
        return False

    sub_page_url = "https://yts-subs.com" + matches[0]
    print(f"Fetching subtitle detail: {sub_page_url}")
    req_sub = urllib.request.Request(sub_page_url, headers={'User-Agent': 'Mozilla/5.0'})
    sub_html = urllib.request.urlopen(req_sub).read().decode('utf-8', errors='ignore')

    zip_match = re.search(r'href="([^"]+\.zip)"', sub_html)
    if not zip_match:
        print("Zip download link not found")
        return False

    zip_url = zip_match.group(1)
    if not zip_url.startswith("http"):
        zip_url = "https://yts-subs.com" + zip_url

    print(f"Downloading subtitle zip: {zip_url}")
    req_zip = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
    zip_bytes = urllib.request.urlopen(req_zip).read()

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for fname in z.namelist():
            if fname.endswith('.srt') or fname.endswith('.vtt'):
                print(f"Extracting: {fname}")
                content = z.read(fname).decode('utf-8', errors='ignore')
                return content

    return False

srt_text = get_yts_subtitles("tt1745960")
if srt_text:
    print("SUCCESS! Length of subtitle content:", len(srt_text))
    with open("D:/Agent_Claudia_Autonomus/goblix/public/subtitles/top-gun-maverick.srt", "w", encoding="utf-8") as f:
        f.write(srt_text)
