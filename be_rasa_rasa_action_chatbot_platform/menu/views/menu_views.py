from rest_framework import generics, permissions
from rest_framework.response import Response
from menu.serializers import MenuSerializer
from menu.models import Menu


class MenuList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MenuSerializer
    queryset = Menu.objects.all()

    def get(self, request, *args, **kwargs):
        menus = self.queryset.all()

        # Function to build tree recursively
        def build_menu_tree(parent_id):
            children = []
            for menu in menus:
                if menu.parentId and menu.parentId.id == parent_id:
                    children.append({
                        "id": menu.id,
                        "nameMenu": menu.nameMenu,
                        "icon": menu.icon,
                        "order": menu.order,
                        "parentId": menu.parentId.id if menu.parentId else None,
                        "url": menu.url,
                        "stt": menu.stt,
                        "children": build_menu_tree(menu.id),
                        "permission": {
                            "add": "true",
                            "view": "true",
                            "edit": "true",
                            "delete": "true",
                            "export": "true",
                            "print": "true"
                        }
                    })
            return children

        # Build the tree starting with root menus (parentId is None)
        list_menus = []
        for menu in menus:
            if not menu.parentId:
                list_menus.append({
                    "id": menu.id,
                    "nameMenu": menu.nameMenu,
                    "icon": menu.icon,
                    "order": menu.order,
                    "parentId": None,
                    "url": menu.url,
                    "stt": menu.stt,
                    "children": build_menu_tree(menu.id)
                })

        return Response(list_menus)


class MenuDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MenuSerializer
    queryset = Menu.objects.all()
