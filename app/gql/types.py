from graphene import ObjectType, String, DateTime, List, Int, Float


class OrderItemObject(ObjectType):
    order_item_id = Int()
    order_id = String()
    book_id = String()
    quantity = Int()
    unit_price = Float()
    total_price = Float()
    added_at = DateTime()


class OrderObject(ObjectType):
    order_id = String()
    user_id = String()
    order_date = DateTime()
    order_status = String()
    added_at = DateTime()
    updated_at = DateTime()
    order_items = List(lambda: OrderItemObject)

    @staticmethod
    def resolve_order_items(root, info):
        return root.order_items


class BookObject(ObjectType):
    book_id = String()
    title = String()
    description = String()
    isbn = String()
    price = Float()
    category = String()
    stock_count = Int()
    added_at = DateTime()
    updated_at = DateTime()
    authors = List(lambda: AuthorObject)
    order_items = List(lambda: OrderItemObject)

    @staticmethod
    def resolve_order_items(root, info):
        return root.order_items

    @staticmethod
    def resolve_authors(root, info):
        return root.authors


class AuthorObject(ObjectType):
    author_id = String()
    first_name = String()
    last_name = String()
    email = String()
    bio = String()
    added_at = DateTime()
    updated_at = DateTime()
    books = List(lambda: BookObject)

    @staticmethod
    def resolve_books(root, info):
        return root.books


class UserObject(ObjectType):
    user_id = String()
    name = String()
    email = String()
    role = String()
    added_at = DateTime()
    updated_at = DateTime()
    orders = List(lambda: OrderObject)

    @staticmethod
    def resolve_orders(root, info):
        return root.orders