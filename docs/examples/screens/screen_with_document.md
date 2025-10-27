```python
from hammett.core import Screen


class DocumentScreen(Screen):
    document = {
        'media': b'This is the text of the document.',
        'document_kwargs': {
            'caption': 'This is the first screen',
            'filename': 'Document.txt',
        },
    }
```
