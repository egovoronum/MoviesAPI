from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from enums.locations import Enum
from typing import Optional

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