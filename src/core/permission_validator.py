from src.common.security import CurrentPersonnel
from src.exc import HTTP_EXC_NOT_AN_ADMIN


class PermissionValidator:
    def __init__(self, admin_route: bool = False):
        self.admin_route = admin_route

    def __call__(self, personnel: CurrentPersonnel):
        if not personnel.is_admin and self.admin_route:
            raise HTTP_EXC_NOT_AN_ADMIN
