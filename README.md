# Data Defenders - CRISP - Cyber Risk Information Sharing Platform

CRISP (Cyber Risk Information Sharing Platform) is a secure threat intelligence sharing platform designed to streamline and enhance threat intelligence sharing among Institutions, particularly in response to increasing ransomware attacks targeting tertiary education institutions.

## 📋 Project Links

- **[Project Management](https://github.com/orgs/COS301-SE-2025/projects/205/views/1)** - scrum board tool github pages
- **[PDF user manual](https://github.com/COS301-SE-2025/CRISP/blob/documents/CRISP%20User%20Manual.pdf)** - **Done by Liam, double check before demo (2025-08-09)**
- **[Technical installation manual]()** - **NEEDS TO BE IMPLEMENTED (2025-08-09)**
- **[Coding standards/quality](https://github.com/COS301-SE-2025/CRISP/wiki/Coding-Standards-Document)** 
- **[Functional Requirements (SRS) Document](https://github.com/COS301-SE-2025/CRISP/blob/documents/SRS.md)** - Detailed system requirements and specifications **NBNB please update(2025-08-13) need updated diagrams , Architectural structural design & requirements , Deployment Model(in progress)**
- **[GitHub Project Board](https://github.com/orgs/COS301-SE-2025/projects/205)** - Track our development progress and sprint planning
- **[Coding standards document](https://github.com/COS301-SE-2025/CRISP/wiki/Coding-Standards-Document)** - **Update the file structure of repo and code before demo(2025-08-09)**

- **[MeetingRecap](https://teams.microsoft.com/l/meetingrecap?driveId=b%21Opdmyntpw0KbT1FIx3jwECKk7kzKq7BMq1KibFpSH3cHq0FaEhGjTZgSi8Ftnxe8&driveItemId=01EMA7DMQOBNOF5AMDGNDIA3YMMZFUOZVY&sitePath=https%3A%2F%2Funiversitypretoria-my.sharepoint.com%2F%3Av%3A%2Fg%2Fpersonal%2Fu22574982_up_ac_za%2FEQ4LXF6BgzNGgG8MZktHZrgBSNTMg3NZ0sg8yjYDV_IZyw&fileUrl=https%3A%2F%2Funiversitypretoria-my.sharepoint.com%2Fpersonal%2Fu22574982_up_ac_za%2FDocuments%2FRecordings%2FMeeting%2520with%2520Mr.%2520AP%2520van%2520der%2520Colf-20250627_155022-Meeting%2520Recording.mp4%3Fweb%3D1&threadId=19%3Ameeting_NDU3Njc0N2EtNTQ3NS00ZjJjLTlmODctNzE5Y2ZlYjkyOTNm%40thread.v2&organizerId=acf38b8a-21c1-4014-9e6d-1995f92463c0&tenantId=ddfa59c8-38d0-49a3-822e-1d3bcb5bf85b&callId=498669da-1962-4b37-b366-9d44e45a8930&threadType=Meeting&meetingType=MeetNow&subType=RecapSharingLink_RecapCore)** 

## 🎯 Project Overview

CRISP addresses the critical need for timely and effective information sharing regarding cybersecurity incidents. By providing a platform for sharing Indicators of Compromise (IoC), Tactics, Techniques, and Procedures (TTP) used by threat actors, as well as mitigation and eradication strategies, CRISP enables institutions to proactively defend against emerging threats.

Inspired by the Malware Information Sharing Platform (MISP) and the CIRCL information sharing community, CRISP serves as BlueVision ITM's solution for providing threat intelligence to clients and partners.

### Key Features

- **Secure Threat Intelligence Sharing** - Standardized threat sharing protocols (STIX/TAXII)
- **Web-based Interface** - Remote access for threat data visualization and management
- **Autonomous Sharing** - Distributed CRISP servers with automated intelligence exchange
- **Data Anonymization** - Configurable anonymization to protect sensitive information
- **External Integration** - Compatible with MISP and other threat intelligence platforms


## 🏗️ Architecture & Design Patterns

CRISP implements several design patterns for a flexible, maintainable, and extensible architecture:

- **Factory Method Pattern** - For STIX object creation and standardization
- **Observer Pattern** - Real-time threat feed notifications
- **Strategy Pattern** - Flexible data anonymization approaches
- **Decorator Pattern** - Enhanced STIX object capabilities, Validation and Exportation

## 🛠️ Technology Stack

### Backend
- **Python** - Core backend development and data processing
- **Django/Django REST Framework** - Web framework and API services
- **PostgreSQL** - Primary database for structured data
- **RabbitMQ** - Message broker for distributed communication

### Security & Threat Intelligence
- **OpenCTI** - Open source threat intelligence platform
- **PyMISP** - MISP integration library
- **STIX2/TAXII2** - Industry-standard threat sharing protocols
- **JWT** - Secure API authentication

### Frontend
- **React.js** - User interface development
- **D3.js** - Data visualization and threat actor network mapping
- **Material-UI** - Professional UI components

### DevOps & Security
- **Docker & Docker Compose** - Containerization and orchestration
- **Nginx** - Web server and reverse proxy
- **OWASP ZAP** - Security testing
- **HashiCorp Vault** - Secrets management

## GitFlow Branching Strategy

Our team follows the GitFlow branching model to ensure organized, secure, and collaborative development for the CRISP platform. This strategy aligns with our security-first development approach and supports our 2-week sprint cycles.
Key Branches:

 - **Main/Master:** Production-ready code with stable releases
 - **Develop:** Integration branch for ongoing development work
 - **Feature branches:** Individual features developed in isolation (feature/*)
 - **Release branches:** Preparation for production releases (release/*)
 - **Hotfix branches:** Critical fixes for production issues (hotfix/*)

## 👥 Team Members

### Armand van der Colf - Full Stack Developer
**Email:** u22574982@tuks.co.za  
**GitHub:** [@Githubber0101](https://github.com/Githubber0101)  
**LinkedIn:** [armand-van-der-colf](https://linkedin.com/in/armand-van-der-colf)

*Versatile full stack developer with strong cybersecurity foundations. Experienced in establishing startups and developing secure web solutions. Specializes in security implementation, threat analysis, and system architecture.*

**Key Skills:** Python, Java, C++, API Design, Database Management, Security Implementation, Kali Linux

---

### Jadyn Stoltz - AI/ML Systems Engineer & Deep Learning Specialist
**Email:** u22609653@tuks.co.za  
**GitHub:** [@JadynTuks](https://github.com/JadynTuks)  
**LinkedIn:** [jadyn-stoltz-9397b1244](https://linkedin.com/in/jadyn-stoltz-9397b1244/)

*Computer science specialist in machine learning and artificial intelligence. Builds intelligent systems for complex threat detection and analysis problems.*

**Key Skills:** Machine Learning, TensorFlow, PyTorch, Data Science, Backend Development, Model Deployment

---

### Diaan Botes - Full Stack Developer & Data Scientist
**Email:** u22598538@tuks.co.za  
**GitHub:** [@DiaanBotes](https://github.com/DiaanBotes)  
**LinkedIn:** [diaan-botes-076267356](https://linkedin.com/in/diaan-botes-076267356/)

*Highly versatile full-stack developer with expertise in backend development, data science, and security. Capable of complete system integration from database to frontend.*

**Key Skills:** C++, Java, Python Data Science, Security (PyJWT, OWASP), API Development, React

---

### Liam van Kasterop - Full-Stack Developer (Backend Focus)
**Email:** u22539761@tuks.co.za  
**GitHub:** [@Liamvk1](https://github.com/Liamvk1)  
**LinkedIn:** [liam-vankasterop-a598b7231](https://linkedin.com/in/liam-vankasterop-a598b7231/)

*Backend-focused full-stack developer passionate about designing robust, secure, and maintainable server-side architectures. Experienced in scalable production systems.*

**Key Skills:** Java, Python, Go, PostgreSQL, Docker, Kubernetes, CI/CD, Security & Performance Optimization

---

### Dreas Vermaak - Backend Developer
**Email:** u22497618@tuks.co.za  
**GitHub:** [@Dreasvermaak](https://github.com/Dreasvermaak)  
**LinkedIn:** [christiaanvermaak-2b961029b](https://linkedin.com/in/christiaanvermaak-2b961029b)

*Experienced backend developer with expertise across multiple programming languages. Specializes in Java and C/C++ development with strong API integration capabilities.*

**Key Skills:** Java, C/C++, Python, API Design, Full-Stack Integration, System Architecture

## 📈 Development Methodology

We follow an **Agile Scrum Framework**:

- **Sprint Duration:** 1 weeks
- **Daily Stand-ups:** 15-minute progress meetings
- **Security-First Approach:** Integrated security testing throughout development
- **Continuous Integration:** Automated testing and security scanning
- **Client Communication:** Weekly meetings and regular feedback loops

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+

### Installation
```
 **FIX AFTER DONE WITH IMPLEMENTATION (add description on how to use system)**
```

## 🔒 Security

CRISP is built with security as a primary concern:
- End-to-end encryption for threat intelligence data
- Configurable anonymization protocols
- Secure API authentication with JWT
- Regular security scanning and vulnerability assessments
- Compliance with threat intelligence sharing standards


## 📞 Contact

**Client:** BlueVision ITM  
**Contact:** Ivan Burke - ib@bitm.co.za

**Development Team:** Data Defenders  
**Contact:** datadefenders.sa@gmail.com
---
