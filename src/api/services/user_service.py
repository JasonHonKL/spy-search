from datetime import date
from sqlalchemy.orm import Session
from ..models.user import Base, User

class UserService:
    @staticmethod
    def get_or_create_user(db: Session, user_data: dict) -> User:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if not user:
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                picture=user_data["picture"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Reset daily tokens if it's a new day
            if user.last_token_reset < date.today():
                user.daily_tokens = 20
                user.last_token_reset = date.today()
                db.commit()
        
        return user
    
    @staticmethod
    def check_and_deduct_tokens(db: Session, user_email: str, tokens_needed: int) -> bool:
        try:
            # Use with_for_update to lock the row for update
            user = db.query(User).filter(User.email == user_email).with_for_update().first()
            if not user:
                return False
                
            # Reset daily tokens if it's a new day
            if user.last_token_reset < date.today():
                user.daily_tokens = 20
                user.last_token_reset = date.today()
            
            if user.daily_tokens >= tokens_needed:
                user.daily_tokens -= tokens_needed
                db.flush()  # Flush changes to database
                db.commit()
                return True
            else:
                return False
                
        except Exception as e:
            db.rollback()  # Rollback on any error
            print(f"Error in check_and_deduct_tokens: {e}")
            return False