from rest_framework.pagination import CursorPagination

class MyBlogPagination(CursorPagination):
    page_size = 3
    ordering =["id"]
    
