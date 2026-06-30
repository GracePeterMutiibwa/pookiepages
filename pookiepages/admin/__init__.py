from pookiepages.admin.discovery import excludeFromAdmin, discoverModels
from pookiepages.admin.views import registerAdminRoutes


class _Admin:
    def exclude(self, model_class: type) -> type:
        return excludeFromAdmin(model_class)


admin = _Admin()

__all__ = ["admin", "registerAdminRoutes", "discoverModels"]
