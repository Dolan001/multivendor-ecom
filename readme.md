# Potential Inc

## MultiVendor

---

# Django ASGI Application Setup Guide

This guide will walk you through setting up and running a Django application using ASGI (Asynchronous Server Gateway
Interface).

## Prerequisites

Before getting started, make sure you have the following installed:

- Python (3.10 recommended)

## Local Setup

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
https://github.com/Dolan001/multivendor-ecom.git
cd dir_name
```

### Step 2: Create a Virtual Environment

Create and activate a virtual environment to isolate your project dependencies:

```bash
python3 -m venv env
source env/bin/activate      # On Unix or MacOS
# OR
env\Scripts\activate         # On Windows
```

### Step 3: Install Dependencies

Install the required Python dependencies using pip:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Django Application

Run the Django application using the ASGI server:

```bash
python manage.py runserver
```
