import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


PAT_WITH_BRACE = re.compile(r'^■(?P<term>.*?)\s\s\{[^}]+\}\s:\s')
PAT_SIMPLE = re.compile(r'^■(?P<term>.*?)\s:\s')

NS = {
    'd': 'http://www.apple.com/DTDs/DictionaryService-1.0.rng',
    'x': 'http://www.w3.org/1999/xhtml',
}


def extract_headword(line: str) -> Optional[str]:
    line = line.rstrip('\n')
    if not line.startswith('■'):
        return None

    m = PAT_WITH_BRACE.match(line)
    if m:
        return m.group('term').strip()

    m = PAT_SIMPLE.match(line)
    if m:
        return m.group('term').strip()

    return None


def extract_headwords(path: Path) -> set[str]:
    with path.open('r', encoding='utf-8') as f:
        headwords = set()
        for line in f:
            headword = extract_headword(line)
            if headword:
                headwords.add(headword)

    return headwords


def extract_titles(path: Path) -> set[str]:
    tree = ET.parse(path)
    root = tree.getroot()
    titles = []
    for entry in root.findall('d:entry', NS):
        title = entry.get('{%s}title' % NS['d'])
        if title:
            titles.append(title)

    return set(titles)


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv or len(argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <dictionary.txt> <dictionary.xml>")
        sys.exit(1)    

    text_path = Path(argv[0])
    headwords = extract_headwords(text_path)

    xml_path = Path(argv[1])
    titles = extract_titles(xml_path)

    print(f"Number of headwords in text: {len(headwords)}")
    print(f"Number of titles in XML: {len(titles)}")

    # Find titles that are not in headwords
    missing_in_headwords = sorted(t for t in titles if t not in headwords)

    # Find headwords that are not in titles
    missing_in_titles = sorted(h for h in headwords if h not in titles)

    print(f"Headwords in text but not in titles ({len(missing_in_titles)}):")
    print('\n'.join(missing_in_titles))
    print()
    print(f"Titles in XML but not in headwords ({len(missing_in_headwords)}):")
    print('\n'.join(missing_in_headwords))
