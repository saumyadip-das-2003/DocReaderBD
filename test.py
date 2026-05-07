import json
import sys

from dotenv import load_dotenv

load_dotenv()

from docreaderbd import DocReader


reader = DocReader()
path = sys.argv[1] if len(sys.argv) > 1 else "test_image.jpg"
result = reader.read(path, verbose=True)

print("\n" + "=" * 50)
print(f'Document type:    {result["document_type"]}')
print(f'Extraction mode:  {result["extraction_mode"]}')
print(f'Fields extracted: {len(result["fields"])}')
print("=" * 50)
for k, v in result["fields"].items():
    print(f"  {k:<30} {v}")
print("=" * 50)
print("\nFull JSON:")
print(
    json.dumps(
        {k: v for k, v in result.items() if k != "ocr_results"},
        ensure_ascii=False,
        indent=2,
    )
)

img = reader.visualize(path, result, save_path="output.jpg")
print("\nAnnotated image saved to output.jpg")
