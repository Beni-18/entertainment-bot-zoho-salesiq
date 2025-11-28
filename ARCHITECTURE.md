# Entertainment Bot - System Architecture & Design

## Overview

**EntertainmentBuddy** is a multi-flow conversational AI chatbot built on Zoho SalesIQ Scripts (Deluge) for entertainment recommendations and event booking.

### Technology Stack
- **Bot Platform**: Zoho SalesIQ Scripts
- **Programming Language**: Deluge
- **Authentication**: OAuth 2.0 (third-party APIs)
- **Third-party APIs**:
  - TMDB (The Movie Database) - Movies
  - Ticketmaster - Events, Concerts, Talkshows
  - Zomato - Food & Restaurants
  - OpenAI - AI-powered mood detection

## System Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  User Interface                              │
│  (SalesIQ Chat Widget)                       │
└────────────────┬──────────────────────────────┘
                 │
        ┌────────▼────────┐
        │  SalesIQ Bot    │
        │  (Main Handler) │  ← Deluge Scripts
        │  - on_chat_open │
        │  - on_message   │
        │  - on_event     │
        └────┬───┬───┬────┘
             │   │   │
    ┌────────▼─┐ │   └──────────┐
    │          │ │              │
    ▼          ▼ ▼              ▼
┌────────┐ ┌───────────┐ ┌──────────┐
│ Plug 1 │ │ Plug 2    │ │ Plug 3   │
│ Movies │ │ Events    │ │ Food     │
└───┬────┘ └─────┬─────┘ └────┬─────┘
    │            │            │
    └────────────┼────────────┘
                 │
        ┌────────▼────────────┐
        │  OAuth 2.0 Conn     │
        │  (Zoho Accounts)    │
        └────────┬────────────┘
                 │
    ┌────────────┼────────────┬───────────┐
    │            │            │           │
    ▼            ▼            ▼           ▼
┌──────┐    ┌──────────┐   ┌────────┐   ┌────────┐
│ TMDB │    │Ticketmas │   │ Zomato │   │ OpenAI │
│      │    │ter+Maps  │   │        │   │        │
└──────┘    └──────────┘   └────────┘   └────────┘
```

## Three Main Flows

### 1. Suggest Something Flow
```
User: "Suggest something"
  ↓
Bot: Show categories (Movies, Books, Games, Food)
  ↓
User: Select "Movies"
  ↓
Bot: Ask preferences (Genre, Rating, Year)
  ↓
User: Select preferences
  ↓
Call: get_movie_suggestions Plug (via TMDB)
  ↓
Bot: Display carousel of 5 movies with ratings and links
```

### 2. Book an Event Flow
```
User: "Book an event"
  ↓
Bot: Show event types (Movies, Concerts, Talkshows, Find nearby)
  ↓
User: Select "Movies"
  ↓
Bot: Ask location and date
  ↓
User: Provide inputs
  ↓
Call: get_events_near_me Plug (via Ticketmaster)
  ↓
Bot: Display carousel of available movie shows
  ↓
User: Click "Book Tickets" → External booking link
```

### 3. Surprise Me Flow (AI-Powered)
```
User: "Surprise me"
  ↓
Bot: Mood Quiz
  Q1: "What's your mood?" (Chill, Excited, Romantic, Energetic, Bored)
  Q2: "Time available?" (30 mins, 1-2 hours, 3+ hours)
  Q3: "Who's with you?" (Alone, Friends, Family, Date)
  ↓
User: Provides answers
  ↓
Call: OpenAI API with prompt containing mood + time + company
  ↓
OpenAI returns: Suggested movie, restaurant, event
  ↓
Call: Other Plugs to fetch real data
  - get_movie_suggestions (movie from AI suggestion)
  - get_food_suggestions (restaurant from AI suggestion)
  - get_events_near_me (event from AI suggestion)
  ↓
Bot: Display "Tonight's Complete Plan" card:
  Section 1: Movie with poster and "Watch trailer" link
  Section 2: Restaurant with ratings and "View menu" link
  Section 3: Event with details and "Get tickets" link
```

## Conversation State Management

```javascript
session_state = {
  current_flow: "suggest" | "book" | "surprise",
  user_preferences: {
    category: "movies",
    genre: "action",
    min_rating: 7,
    year: 2023,
    location: "Mumbai",
    mood: "excited",
    time_available: "3+ hours"
  },
  conversation_context: [],
  recommendations_shown: []
}
```

## Error Handling Strategy

- **API Timeout**: Show cached results or suggest alternatives
- **Rate Limiting**: Queue requests with exponential backoff
- **Invalid Input**: Re-ask question with validation
- **Empty Results**: Suggest broader search parameters

## Performance Optimizations

1. **Caching Layer**
   - Store TMDB results for 24 hours
   - Cache genre lists and mappings
   - Cache location-based events for 6 hours

2. **Lazy Loading**
   - Fetch carousel items on demand
   - Load images after text content
   - Pagination for large result sets

3. **Request Batching**
   - Combine multiple API calls when possible
   - Use webhook connections for real-time updates

## Security Considerations

✅ OAuth 2.0 for all API calls - no hardcoded credentials
✅ Input validation on all user inputs
✅ Rate limiting per user session
✅ No sensitive data in logs
✅ HTTPS for all external API calls

## Deployment Architecture

- **Hosting**: Zoho SalesIQ (Cloud-based)
- **Scalability**: Automatic by Zoho
- **Monitoring**: Zoho Analytics & Logs
- **Backup**: Automatic by Zoho Account
