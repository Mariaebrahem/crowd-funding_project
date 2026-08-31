# Crowd-Funding Web Application

A full-featured Django web application that allows users to create and donate to fundraising campaigns. This platform facilitates the crowd-funding process, connecting project creators with backers in Egypt.

## 🚀 Key Features

### 🔐 Authentication & User Management
- **User Registration & Login:** Secure sign-up and login system with email confirmation.
- **Profile Management:** Users can view and edit their profiles, see their projects and donations, and delete their accounts.
- **Email Activation:** Account activation via email with a 24-hour expiration link.
- **Egyptian Mobile Validation:** Phone number input is validated for Egyptian numbers.

### 💼 Projects & Campaigns
- **Create Projects:** Users can launch campaigns with titles, details, categories, multiple images, tags, and funding targets.
- **Donations & Interactions:** Users can donate to projects, leave comments, and report inappropriate content or comments.
- **Project Ratings & Display:** Projects feature an average rating, a photo slider, and show similar projects based on tags.
- **Admin Features:** Admins can feature projects on the homepage and manage categories.

### 🏠 Dynamic Homepage
- **Curated Content:** Displays highest-rated, latest, and admin-featured projects.
- **Category Browsing:** Users can explore projects by category.
- **Search Functionality:** Search for projects by title or tags.

## 🛠️ Built With
- **Backend:** Django, Django REST Framework (if applicable)
- **Frontend:** HTML, CSS, JavaScript (and likely a framework like Bootstrap)
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **Other Tools:** Celery (for async tasks like emails), Pillow (for image handling)

## 📋 Project Overview
This project was developed as a final comprehensive Django project, implementing core web development concepts including user authentication, database relationships, file uploads, and a responsive UI.
