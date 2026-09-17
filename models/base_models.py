from pydantic import BaseModel, Field
from typing import Optional
from enums.roles import Roles
from datetime import datetime
from enum import Enum
from uuid import UUID

class ApiError(BaseModel):
    message: str | list[str]
    error: str
    statusCode: int

class TestUser(BaseModel):
    email: str = Field(..., min_length=3)
    fullName: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=20)
    passwordRepeat: str = Field(..., min_length=8, max_length=20)
    roles: list[Roles]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

class CreatedUser(BaseModel):
    id: str
    email: str = Field(..., min_length=3)
    fullName: str = Field(..., min_length=1, max_length=255)
    roles: list[Roles]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

class LoggedInUser(BaseModel):
    user: CreatedUser
    accessToken: str
    refreshToken: UUID
    expiresIn: int

class Location(str, Enum):
    MSK = "MSK"
    SPB = "SPB"

class Genre(BaseModel):
    name: str
    id: Optional[int] = None

class ReviewUser(BaseModel):
    fullName: str

class Review(BaseModel):
    userId: str
    text: str
    rating: int = Field(..., ge=0, le=5)
    createdAt: datetime
    user: ReviewUser

class CreateMovieData(BaseModel):
    name: str
    description: str
    genreId: int
    imageUrl: str
    price: int
    location: Location
    published: bool

class Movie(BaseModel):
    id: int
    name: str
    description: str
    genreId: int
    imageUrl: str
    price: int
    rating: float = Field(..., ge=0, le=5)
    location: Location
    published: bool
    createdAt: datetime
    genre: Genre       

class MoviesPage(BaseModel):
    movies: list[Movie]
    count: int
    page: int
    pageSize: int
    pageCount: int

class MovieDetails(Movie):
    reviews: list[Review]