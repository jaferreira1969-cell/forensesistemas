from bs4 import BeautifulSoup
import os

def test_parse():
    file_path = r"c:\Users\Jakelaine Silvestre\Desktop\Forense\imagens\TesteWhatsapp\records.html"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'rb') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    
    print("Searching for 'Message' blocks...")
    divs = soup.find_all('div', class_='t o')
    print(f"Found {len(divs)} 't o' divs total.")
    
    message_count = 0
    for i, div in enumerate(divs):
        title_div = div.find('div', class_='t i')
        if title_div:
            # Get direct text only
            direct_text = ''.join([t for t in title_div.find_all(string=True, recursive=False)]).strip()
            
            if direct_text == 'Message':
                message_count += 1
                print(f"\n--- Message Block #{message_count} found ---")
                message_count += 1
                print(f"\n--- Message Block #{message_count} found ---")
                
                content_container = div.find('div', class_='m')
                if not content_container:
                    print("No content container (.m) found")
                    continue
                
                inner_div = content_container.find('div')
                if not inner_div:
                    print("No inner div found")
                    continue
                
                # Print direct children classes to verify structure
                children = inner_div.find_all('div', recursive=False)
                print(f"Inner div has {len(children)} direct children divs")
                
                fields = inner_div.find_all('div', class_='t o', recursive=False)
                print(f"Found {len(fields)} fields (recursive=False)")
                
                if len(fields) == 0:
                    # Try recursive=True to see if they are deeper
                    fields_recursive = inner_div.find_all('div', class_='t o')
                    print(f"Found {len(fields_recursive)} fields (recursive=True)")
                    
                    # Print first few children to see what they are
                    for child in inner_div.children:
                        if child.name:
                            print(f"Child tag: {child.name}, classes: {child.get('class')}")

                # Try to extract one field
                for field in fields[:3]:
                    k = field.find('div', class_='t i')
                    v = field.find('div', class_='m')
                    if k and v:
                        print(f"Field: {k.get_text(strip=True)} = {v.get_text(strip=True)}")

    print(f"\nTotal 'Message' blocks found: {message_count}")

if __name__ == "__main__":
    test_parse()
