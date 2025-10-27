```python
from hammett.core.permission import Permission


class PaywallPermission(Permission):
    async def handle_permission_denied(self, update, context):
        return await Payment().jump(update, context)

    async def has_permission(self, update, context):
        return has_user_paid(update.effective_user.id)
```
