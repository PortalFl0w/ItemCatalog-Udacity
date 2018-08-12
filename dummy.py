from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from setup import Category, Base, Item, User

engine = create_engine('sqlite:///items.db')
print "Creating Dummy Data..."

# Next we will populate the database with some dummy data
Base.metadata.bind = engine

# Declare database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Dummy User
user1 = User(gid="1", username="Jennifer Tan", picture="/static/jennifer.jpg", email="jentan21231@example.com")
session.add(user1)

# Declare Categories
category_office = Category(name = "Office", owner_id = 1)
category_bedroom = Category(name = "Bedroom", owner_id = 1)
category_kitchen = Category(name = "Kitchen", owner_id = 1)
category_livingroom = Category(name = "Living Room", owner_id = 1)
category_decorations = Category(name = "Decorations", owner_id = 1)
category_bathroom = Category(name = "Bathroom", owner_id = 1)

session.add(category_office)
session.add(category_bedroom)
session.add(category_kitchen)
session.add(category_livingroom)
session.add(category_decorations)
session.add(category_bathroom)

# Office Items
item_office_1 = Item(name = "Mahogany Office Desk", description = "Fantastic solid mahogany desk. 200cm x 100cm x 60cm", price = "1500.00", category = category_office, owner_id = 1)
item_office_2 = Item(name = "Ergonomic Office Chair", description = "Very comfortable office chair, made by ergonomic experts in Italy.", price = "199.99", category = category_office, owner_id = 1)
session.add(item_office_1)
session.add(item_office_2)

# Bedroom Items
item_bedroom_1 = Item(name = "Kingsize Royal Bed", description = "A bed worthy of the royalty!", price = "3999.99", category = category_bedroom, owner_id = 1)
item_bedroom_2 = Item(name = "Pillow Set - 4", description = "Soft Memory Foam Pillows", price = "60", category = category_bedroom, owner_id = 1)
session.add(item_bedroom_1)
session.add(item_bedroom_2)

# Kitchen Items
item_kitchen_1 = Item(name = "Knife Set", description = "Very Sharp Stainless Steel Knives!", price = "65", category = category_kitchen, owner_id = 1)
session.add(item_kitchen_1)

# Living Room Items
item_livingroom_1 = Item(name = "Sofa - 3 Seat", description = "Amazing extra-soft sofa, made in Germany.", price = "499", category = category_livingroom, owner_id = 1)
session.add(item_livingroom_1)

# Decoration Items
item_decorations_1 = Item(name = "Picture Frame - A3 Size", description = "Wooden picture frame with quick-mount feature.", price = "20", category = category_decorations, owner_id = 1)
session.add(item_decorations_1)

# Bathroom Items
item_bathroom_1 = Item(name = "Flusha - Dual Flush Ceramic Toilet", description = "Dual Flush and Quick Flush options! Made in Sweden", price = "399", category = category_bathroom, owner_id = 1)
session.add(item_bathroom_1)

session.commit()

print "Dummy Data Added."
