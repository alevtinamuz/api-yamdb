from django.core.management import BaseCommand
from django.conf import settings

import csv
import os

from reviews.models import User, Category, Genre, Title, Comment, Review

DATA_DIR = os.path.join(settings.BASE_DIR, 'static', 'data')


class Command(BaseCommand):
    help = 'Загружает данные из .csv файлов в базу данных.'

    def handle(self, *args, **options):
        try:
            self.import_users()
            self.import_category()
            self.import_genre()
            self.import_titles()
            self.import_genre_title()
            self.import_review()
            self.import_comments()
            self.stdout.write(self.style.SUCCESS('Импорт данных закончен.'))
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f'Импорт данных не закончен. Ошибка: {error}')
            )

    def _read_csv(self, filename):
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'{filename} отсутствует.'))
            return list()
        with open(path, encoding='utf-8') as file:
            return list(csv.DictReader(file))

    def import_users(self):
        rows = self._read_csv('users.csv')
        users = [
            User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name'],
            ) for row in rows
        ]
        User.objects.bulk_create(users, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Количество пользователей испортировано: {len(users)}'
            )
        )

    def import_category(self):
        rows = self._read_csv('category.csv')
        categories = [
            Category(id=row['id'], name=row['name'], slug=row['slug'])
            for row in rows
        ]
        Category.objects.bulk_create(categories, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Количество категорий импортировано: {len(categories)}'
            )
        )

    def import_genre(self):
        rows = self._read_csv('genre.csv')
        genres = [
            Genre(id=row['id'], name=row['name'], slug=row['slug'])
            for row in rows
        ]
        Genre.objects.bulk_create(genres, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Количество жанров импортировано: {len(genres)}'
            )
        )

    def import_titles(self):
        rows = self._read_csv('titles.csv')
        titles = [
            Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category_id=row['category'],
            )
            for row in rows
        ]
        Title.objects.bulk_create(titles, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Количество произведений импортировано: {len(titles)}'
            )
        )

    def import_genre_title(self):
        rows = self._read_csv('genre_title.csv')
        ThroughModel = Title.genre.through
        links = [
            ThroughModel(
                id=row['id'],
                title_id=row['title_id'],
                genre_id=row['genre_id'],
            )
            for row in rows
        ]
        ThroughModel.objects.bulk_create(links, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Количество связей жанр-произведение импортировано: '
                f'{len(links)}'
            )
        )

    def import_comments(self):
        rows = self._read_csv('comments.csv')
        comments = [
            Comment(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author_id=row['author'],
                pub_date=row['pub_date'],
            )
            for row in rows
        ]
        Comment.objects.bulk_create(comments, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Количество комментариев импортировано: {len(comments)}'
            )
        )

    def import_review(self):
        rows = self._read_csv('review.csv')
        reviews = [
            Review(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author_id=row['author'],
                score=row['score'],
                pub_date=row['pub_date'],
            )
            for row in rows
        ]
        Review.objects.bulk_create(reviews, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Количество отзывов импортировано: {len(reviews)}'
            )
        )
