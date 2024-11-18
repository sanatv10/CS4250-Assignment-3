from bs4 import BeautifulSoup
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["cs_crawler"]
pages_collection = db["pages"]

def parse_faculty_page():
    
    page = pages_collection.find_one({"url": "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"})
    
    if not page:
        print("Faculty page not found in the database!")
        return
    
    html = page["html"]
    soup = BeautifulSoup(html, "html.parser")

    
    faculty_containers = soup.find_all("div", class_="clearfix")
    if not faculty_containers:
        print("Faculty container not found in the HTML!")
        return

    
    faculty_data = []
    for container in faculty_containers:
        name = container.find("h2").get_text(strip=True) if container.find("h2") else "N/A"
        title = container.find("strong", string="Title:").next_sibling.strip() if container.find("strong", string="Title:") else "N/A"
        office = container.find("strong", string="Office:").next_sibling.strip() if container.find("strong", string="Office:") else "N/A"
        phone = container.find("strong", string="Phone:").next_sibling.strip() if container.find("strong", string="Phone:") else "N/A"
        email_tag = container.find("a", href=lambda href: href and "mailto:" in href)
        email = email_tag.get_text(strip=True) if email_tag else "N/A"
        web_tag = container.find("a", href=lambda href: href and "cpp.edu/faculty" in href)
        web = web_tag["href"].strip() if web_tag else "N/A"

        faculty_data.append({
            "name": name,
            "title": title,
            "office": office,
            "phone": phone,
            "email": email,
            "web": web
        })

    if not faculty_data:
        print("No faculty data found to persist.")
        return

    
    faculty_info_collection = db["faculty_info"]
    faculty_info_collection.insert_many(faculty_data)
    print(f"Inserted {len(faculty_data)} faculty records into the faculty_info collection.")


parse_faculty_page()
