"""Reproducible sample college-library knowledge base."""
from knowledge_base import Fact

def sample_facts():
    facts = []
    def add(p, *a): facts.append(Fact(p, tuple(a)))
    subjects = ["Artificial_Intelligence","Data_Structures","Database_Systems","Computer_Networks",
                "Operating_Systems","Software_Engineering","Mathematics","Cyber_Security"]
    for s in subjects: add("Subject", s)
    authors = [
        ("Russell","Artificial_Intelligence"),("Norvig","Artificial_Intelligence"),
        ("Cormen","Data_Structures"),("Sedgewick","Data_Structures"),
        ("Elmasri","Database_Systems"),("Kurose","Computer_Networks"),
        ("Tanenbaum","Operating_Systems"),("Sommerville","Software_Engineering"),
        ("Rosen","Mathematics"),("Stallings","Cyber_Security")]
    for a,s in authors:
        add("Author",a); add("SpecializesIn",a,s)
    books = [
        ("AI_A_Modern_Approach","Russell","Artificial_Intelligence"),
        ("Artificial_Intelligence_Foundations","Norvig","Artificial_Intelligence"),
        ("Introduction_to_Algorithms","Cormen","Data_Structures"),
        ("Algorithms_in_C","Sedgewick","Data_Structures"),
        ("Fundamentals_of_Database_Systems","Elmasri","Database_Systems"),
        ("Computer_Networking","Kurose","Computer_Networks"),
        ("Modern_Operating_Systems","Tanenbaum","Operating_Systems"),
        ("Software_Engineering","Sommerville","Software_Engineering"),
        ("Discrete_Mathematics","Rosen","Mathematics"),
        ("Network_Security_Essentials","Stallings","Cyber_Security"),
        ("Deep_Learning_Basics","Norvig","Artificial_Intelligence"),
        ("Advanced_Data_Structures","Cormen","Data_Structures"),
        ("Database_Design","Elmasri","Database_Systems"),
        ("Secure_Computer_Networks","Stallings","Cyber_Security"),
        ("Software_Project_Management","Sommerville","Software_Engineering")]
    for b,a,s in books:
        add("Book",b); add("WrittenBy",b,a); add("BelongsTo",b,s)
    students = ["Ravi","Ananya","Kiran","Meera","Arjun","Divya","Rahul","Sneha","Vikram","Pooja"]
    depts = ["Computer_Science","Information_Science","Electronics","Mechanical"]
    for i,st in enumerate(students):
        add("Student",st); add("MemberOf",st,depts[i%len(depts)])
    faculty = ["Dr_Sharma","Dr_Rao","Prof_Mehta","Dr_Kulkarni","Prof_Iyer"]
    for f in faculty: add("Faculty",f)
    for f,d in zip(faculty,depts+["Computer_Science"]):
        add("MemberOf",f,d)
    for d in depts: add("Department",d)
    borrowers = [
        ("Ravi","AI_A_Modern_Approach"),("Ananya","Introduction_to_Algorithms"),
        ("Kiran","Computer_Networking"),("Meera","Fundamentals_of_Database_Systems"),
        ("Arjun","Modern_Operating_Systems"),("Divya","Software_Engineering"),
        ("Rahul","Discrete_Mathematics"),("Sneha","Network_Security_Essentials"),
        ("Vikram","Algorithms_in_C"),("Pooja","Database_Design"),
        ("Dr_Sharma","Deep_Learning_Basics"),("Dr_Rao","Advanced_Data_Structures"),
        ("Prof_Mehta","Secure_Computer_Networks"),("Dr_Kulkarni","Software_Project_Management"),
        ("Prof_Iyer","AI_A_Modern_Approach"),
        ("Ravi","Computer_Networking"),("Ananya","Database_Design"),
        ("Kiran","Discrete_Mathematics"),("Meera","AI_A_Modern_Approach"),
        ("Arjun","Network_Security_Essentials")]
    for p,b in borrowers: add("Borrowed",p,b)
    return facts
