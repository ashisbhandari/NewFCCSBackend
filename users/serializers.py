from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to the token
        token['userID'] = user.userID
        token['email'] = user.email
        token['ownerName'] = user.ownerName
        token['companyName'] = user.companyName
        token['is_staff'] = user.is_staff
        token['country'] = user.country
        token['city'] = user.city
        
        return token

def get_tokens_for_user(user):
    """
    Generate JWT tokens with custom claims for a user
    """
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims to both access and refresh tokens
    refresh['userID'] = user.userID
    refresh['email'] = user.email
    refresh['ownerName'] = user.ownerName
    refresh['companyName'] = user.companyName
    refresh['is_staff'] = user.is_staff
    refresh['country'] = user.country
    refresh['city'] = user.city
    
    # Access token automatically inherits custom claims from refresh token
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
