from django.contrib.auth import get_user_model
from viewer.models import AddAuction, Bid, Category, UserAccounts, AccountType, AuctionImage, About, BuyerEvaluation, SellerEvaluation
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.files import File
from datetime import timedelta
import random
import os


class Command(BaseCommand):
    help = 'Naplní databázi výchozími daty'

    def handle(self, *args, **kwargs):
        self.PHOTO_DIR = 'media/photos/'
        self.SAVE_DIR = 'photos_add_auction/'

        if not os.path.exists(self.PHOTO_DIR):
            self.stdout.write(self.style.WARNING(f"Adresář '{self.PHOTO_DIR}' neexistuje."))
            return

        self.photos = [f for f in os.listdir(self.PHOTO_DIR) if f.endswith(('.jpg', '.gif', '.png'))]

        AccountType.objects.get_or_create(account_type='User')
        AccountType.objects.get_or_create(account_type='Premium')

        categories = self.create_default_categories()
        users = self.create_default_users()

        sample_descriptions = {
            'Paintings': ["A beautiful piece of art from the 18th century.", "An exquisite oil painting with vibrant colors."],
            'Statues': ["A stunning ancient statue with a rich history.", "A captivating bronze sculpture."],
            'Numismatics': ["Rare coins from the medieval era.", "Silver and gold coins dating back to the Roman Empire."],
            'Jewelry': ["Elegant and unique piece of jewelry, perfect for collectors.", "A dazzling emerald ring set in gold."]
        }
        sample_names = {
            'Paintings': ["Classic Painting", "Sunset Portrait"],
            'Statues': ["Ancient Statue", "Mythical Creature"],
            'Numismatics': ["Golden Coin", "Silver Coin Set"],
            'Jewelry': ["Ruby Necklace", "Emerald Ring"]
        }
        categorized_photos = {
            'Paintings': [f for f in self.photos if f.startswith('obraz')],
            'Statues': [f for f in self.photos if f.startswith('socha')],
            'Numismatics': [f for f in self.photos if f.startswith('mince')],
            'Jewelry': [f for f in self.photos if f.startswith('šperk')]
        }

        self.create_all_auctions(users, categories, sample_names, sample_descriptions, categorized_photos)

        self.stdout.write(self.style.SUCCESS('Hotovo!'))

    def create_default_categories(self):
        categories = ['Paintings', 'Statues', 'Numismatics', 'Jewelry']
        category_objects = []
        for category_name in categories:
            category, _ = Category.objects.get_or_create(name=category_name)
            category_objects.append(category)
        return category_objects

    def get_or_create_user(self, username, email):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password('1234')
            user.save()
        return user

    def create_default_users(self):
        user_model = get_user_model()
        premium_nicks = ["SkylineWalker", "ThunderBlade", "MysticVoyager", "PixelCrafter", "ShadowHunter23", "NeonNinja", "BlazeRunner", "1234"]
        user_nicks = ["FrozenPhoenix", "CyberSailor", "EchoJumper", "IronWolfX", "CosmicRider", "LunarKnight7", "SwiftFalcon", "CrimsonEcho"]
        users = []

        superuser, created = user_model.objects.get_or_create(
            username='1234',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            superuser.set_password('1234')
            superuser.save()
        users.append(superuser)

        team = [
            ("Martin Praguer", "martin.praguer@gmail.com", "Martin Praguer.png", "populate data", "templates and details", "https://www.linkedin.com/in/martinpraguer/"),
            ("Andrej Schön", "a.schon@seznam.cz", "Andrej Schön.jpg", "account administration", "shopping cart", "https://www.linkedin.com/in/andrej-sch%C3%B6n-032893333/"),
            ("Ondřej Vitásek", "ondrasek11vitasek@seznam.cz", "Ondřej Vitásek.jpg", "morale boost", "tester", "")
        ]
        for name, email, photo, lock2, lock3, link in team:
            user = self.get_or_create_user(username=name, email=email)
            if not About.objects.filter(about_user=user).exists():
                About.objects.create(
                    photo=f'about_us/{photo}',
                    about_user=user,
                    contact=email,
                    locket1='Role in the project:',
                    locket2=lock2,
                    locket3=lock3,
                    locket4='',
                    locket5=link
                )
            users.append(user)

        account_premium, _ = AccountType.objects.get_or_create(account_type='Premium')
        for username in premium_nicks:
            if username == '1234':
                continue
            user, created = user_model.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            if created:
                user.set_password('1234')
                user.save()
            UserAccounts.objects.get_or_create(user=user, account_type=account_premium, is_premium=True)
            users.append(user)

        for username in user_nicks:
            user, created = user_model.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            if created:
                user.set_password('1234')
                user.save()
            users.append(user)

        return users

    def add_auction_images(self, auction, category_photos):
        num_images = random.randint(1, 3)
        selected_photos = random.sample(category_photos, min(num_images, len(category_photos)))
        for photo in selected_photos:
            photo_path = os.path.join(self.PHOTO_DIR, photo)
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as photo_file:
                    auction_image = AuctionImage(auction=auction)
                    auction_image.image.save(os.path.join(self.SAVE_DIR, photo), File(photo_file), save=True)

    def generate_auction_dates(self, expired):
        if expired:
            start_date = timezone.now() - timedelta(days=random.randint(7, 14))
        else:
            start_date = timezone.now() - timedelta(days=random.randint(0, 6))
        end_date = start_date + timedelta(days=7)
        return start_date, end_date

    def generate_evaluation(self, auction, seller, buyer):
        seller_rating = random.randint(1, 5)
        buyer_rating = random.randint(1, 5)
        seller_comments = [
            "The buyer was very prompt and polite.",
            "Smooth transaction, would recommend.",
            "Quick payment, easy communication."
        ]
        buyer_comments = [
            "The item was as described, fast delivery.",
            "Seller was very professional and helpful.",
            "Great experience, would buy again!"
        ]
        BuyerEvaluation.objects.create(
            auction=auction,
            buyer=buyer,
            buyer_rating=buyer_rating,
            buyer_comment=random.choice(buyer_comments),
        )
        SellerEvaluation.objects.create(
            auction=auction,
            seller=seller,
            seller_rating=seller_rating,
            seller_comment=random.choice(seller_comments),
        )

    def create_all_auctions(self, users, categories, sample_names, sample_descriptions, categorized_photos):
        setups = [
            ('buy_now', 'without_premium', True, 5),
            ('buy_now', 'without_premium', False, 30),
            ('place_bid', 'premium', True, 5),
            ('place_bid', 'premium', False, 30),
            ('place_bid', 'without_premium', True, 5),
            ('place_bid', 'without_premium', False, 30),
        ]
        for auction_type, premium, expired, count in setups:
            self.create_auctions_without_bids(users, categories, auction_type, premium, expired, count, sample_names, sample_descriptions, categorized_photos)
            self.create_auctions_with_bids(users, categories, auction_type, premium, expired, count, sample_names, sample_descriptions, categorized_photos)

    def create_auctions_without_bids(self, users, categories, auction_type, premium, expired, count, sample_names, sample_descriptions, categorized_photos):
        for _ in range(count):
            user = random.choice(users)
            category = random.choice(categories)
            name_auction = random.choice(sample_names[category.name])
            description = random.choice(sample_descriptions[category.name])
            start_price = random.randint(1000, 100000)
            auction_start_date, auction_end_date = self.generate_auction_dates(expired)

            auction = AddAuction.objects.create(
                user_creator=user,
                category=category,
                name_auction=name_auction,
                description=description,
                auction_type=auction_type,
                price=start_price if auction_type == 'place_bid' else None,
                start_price=start_price if auction_type == 'place_bid' else None,
                buy_now_price=random.randint(1000, 100000) if auction_type == 'buy_now' else None,
                minimum_bid=random.randint(500, 1000) if auction_type == 'place_bid' else None,
                promotion=(premium == 'premium'),
                auction_start_date=auction_start_date,
                auction_end_date=auction_end_date,
                is_sold=False,
                number_of_views=random.randint(0, 1000),
            )
            self.add_auction_images(auction, categorized_photos[category.name])

    def create_auctions_with_bids(self, users, categories, auction_type, premium, expired, count, sample_names, sample_descriptions, categorized_photos):
        for _ in range(count):
            user = random.choice(users)
            category = random.choice(categories)
            name_auction = random.choice(sample_names[category.name])
            description = random.choice(sample_descriptions[category.name])
            start_price = random.randint(1000, 100000)
            auction_start_date, auction_end_date = self.generate_auction_dates(expired)

            auction = AddAuction.objects.create(
                user_creator=user,
                category=category,
                name_auction=name_auction,
                description=description,
                auction_type=auction_type,
                price=start_price if auction_type == 'place_bid' else None,
                start_price=start_price if auction_type == 'place_bid' else None,
                buy_now_price=random.randint(1000, 100000) if auction_type == 'buy_now' else None,
                minimum_bid=random.randint(500, 1000) if auction_type == 'place_bid' else None,
                promotion=(premium == 'premium'),
                auction_start_date=auction_start_date,
                auction_end_date=auction_end_date,
                is_sold=False,
                number_of_views=random.randint(0, 1000),
            )
            self.add_auction_images(auction, categorized_photos[category.name])

            if auction_type == 'buy_now':
                auction.name_buyer = random.choice(users)
                auction.is_sold = True
                auction.save()
                if expired:
                    self.generate_evaluation(auction, auction.user_creator, auction.name_buyer)
            elif auction_type == 'place_bid':
                current_price = start_price
                num_bids = random.randint(1, 10)
                last_bidder = None
                for _ in range(num_bids):
                    bidder = random.choice(users)
                    last_bidder = bidder
                    min_bid_increment = auction.minimum_bid
                    bid_amount = random.randint(min_bid_increment, min_bid_increment + 2000)
                    auction.previous_price = current_price
                    current_price += bid_amount
                    Bid.objects.create(
                        auction=auction,
                        user=bidder,
                        amount=bid_amount,
                        price=current_price,
                        timestamp=timezone.now()
                    )
                if expired and last_bidder:
                    auction.name_buyer = last_bidder
                    auction.is_sold = True
                    auction.save()
                    self.generate_evaluation(auction, auction.user_creator, auction.name_buyer)
                elif not expired and last_bidder:
                    auction.name_bider = last_bidder
                auction.price = current_price
                auction.save()