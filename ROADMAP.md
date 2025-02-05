# 📌 OELMs Roadmap
_Last Updated: 5 February 2025_

💬 **Community Discussions:** [Discord](https://discord.gg/vSPvgyVxJ7)  

## 🎯 Vision Statement
Open Educational Language Models (OELMs, pronounced like the tree "elms") combine the technical power of generative AI with the participatory power of open education to make learning more affordable, effective, and meaningful. While the first OELMs will access LLMs running in the cloud, eventually OELMs should run completely locally on learners' devices.

## 🚀 Roadmap Overview
We welcome contributions — whether it's code, documentation, or ideas! If you're interested, check out our **[Guide to Contributing](CONTRIBUTING.md)** below.  

### ✅ Completed
🎉 Features we've shipped!  
- Simple mobile-first web UI
- Separation of system prompt stub, content, and activity instructions as text files so non-technical instructors can contribute
- Aggregation of system prompt stub, content, and activity instructions into system prompt
- Working chat via Groq API

## 🔨 In Progress (Next Release)
We’re actively working on these features. Please contribute!  

📝 **Documentation Updates**  
- [Installation Guide](/issues/2)
- [OELMs Content Creation Guide](/issues/3)

## 📌 Upcoming
These are features we're planning. Share your feedback or vote on priorities in [Discussions](/discussions).  

**Initial Research Infrastructure**
- Capture user feedback (e.g., thumbs up / thumbs down)
- Capture anonymized chat transcripts  

**Authoring Enhancements**
- Web-based authoring interface for creating courses
- Change course storage from text files to sqlite database
- Create a system for instructors to upload a zip file, verify its structure, and import into the sqlite db

**LTI Provider (LTI tool) Functionality**
- Authenticate users
- Group users by LMS section

**Initial Instructor Tools**
- Select a combination of content and activity and receive a URL students can use to bypass the TOC-TOP views and go straight to the chat
- See an OELM-generated synthesis of student conversations for a given chapter, in order to adapt outside-of-OELM (OOO) instruction according to students’ understanding

## 💡 Ideas & Community Wishlist
Suggest new feature ideas in [Discussions](/discussions)!

## 🤝 Contribution Guide
Want to contribute? Follow these steps:  

1. **Check Issues:** Look for a "good first issue" tag in[Issues](https://github.com/kalendar/oelm/issues).
2. **Join Discussions:** Share your ideas in our [Discord](https://discord.gg/vSPvgyVxJ7).
3. **Fork & Code:** Follow our [Guide to Contributing](CONTRIBUTING.md) to submit pull requests.
4. **Get Recognized:** We highlight top contributors in our release notes! 🎉  

<!--//
## 📢 Stay Updated
🔹 Follow us on **[Twitter/LinkedIn/GitHub](Link)** for updates.  
📩 Join our **[newsletter](Link)** to get release notes.  
📆 Attend our **monthly community call** ([sign up](Link)).  
//-->