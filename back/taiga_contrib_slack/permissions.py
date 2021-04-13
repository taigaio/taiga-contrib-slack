from taiga.base.api.permissions import (TaigaResourcePermission, IsProjectAdmin,
                                        AllowAny)


class SlackHookPermission(TaigaResourcePermission):
    retrieve_perms = IsProjectAdmin()
    create_perms = IsProjectAdmin()
    update_perms = IsProjectAdmin()
    destroy_perms = IsProjectAdmin()
    list_perms = AllowAny()
    test_perms = IsProjectAdmin()
