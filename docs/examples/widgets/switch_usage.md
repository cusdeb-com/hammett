```python
async def switch(self, update, context, selected_choice):
    code, _ = selected_choice
    # your logic ...

    return await super().switch(update, context, selected_choice)
```
