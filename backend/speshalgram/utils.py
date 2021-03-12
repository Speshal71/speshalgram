from django.db.models import PositiveIntegerField, Subquery


class SubqueryCount(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) as sq)"
    output_field = PositiveIntegerField()


class PermissionsByActionsMixin:
    permission_classes_by_actions = {}
    
    def get_permissions(self):
        try:
            return [
                perm()
                for perm in self.permission_classes_by_actions[self.action]
            ]
        except KeyError:
            return super().get_permissions()
