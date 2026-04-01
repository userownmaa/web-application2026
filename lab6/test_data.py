from models import db, User, Course, Review
from datetime import datetime, timedelta
import random

teachers = db.session.execute(db.select(User)).scalars().all()
courses = db.session.execute(db.select(Course)).scalars().all()



all_reviews = []

for course in courses:
    
    num_reviews = random.randint(3, 10)
    
    for i in range(num_reviews):
        rating = random.randint(0, 5)
        
        if rating == 5:
            text = "отзыв 5 звезд"
        elif rating == 4:
            text = "отзыв 4 звезды"
        elif rating == 3:
            text = "отзыв 3 звезды"
        elif rating == 2:
            text = "отзыв 2 звезды"
        elif rating == 1:
            text = "отзыв 1 звезда"
        else:
            text = "отзыв 0 звезд"
        
        user = random.choice(teachers)
        
        days_ago = random.randint(1, 180)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        review = Review(
            rating=rating,
            text=text,
            course_id=course.id,
            user_id=user.id,
            created_at=created_at
        )
        db.session.add(review)
        all_reviews.append(review)
        
        course.rating_sum += rating
        course.rating_num += 1
        
        

db.session.commit()



test_user = User(
    first_name='Тест',
    last_name='Тестов',
    middle_name='Тестович',
    login='test',
    created_at=datetime.now()
)
test_user.set_password('test123')  

db.session.add(test_user)
db.session.commit()
