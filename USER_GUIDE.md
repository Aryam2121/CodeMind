# 🎯 Smart City AI Assistant - User Guide

## Quick Start - What Can You Do?

Your Smart City AI Assistant has **4 main features**. Here's exactly what to do with each:

---

## 1️⃣ **AI Chat** - Ask Questions About City Policies

**URL**: http://localhost:3000/chat

### What You Can Do:
- Ask questions about city policies, procedures, and regulations
- Get answers with source citations from uploaded documents
- Query information from the knowledge base

### How to Use:
1. Click on the **"AI Chat"** blue card on the homepage
2. Type your question in the text box at the bottom
3. Press Enter or click **"Send"**
4. Wait for the AI to respond with an answer

### Example Questions to Try:
```
"What are the water quality standards?"
"How long does it take to repair potholes?"
"What is the procedure for handling water complaints?"
"How often should water tanks be cleaned?"
"What are the priority levels for pothole repairs?"
```

### What You'll See:
- Your question on the right side
- AI's answer on the left side
- Source documents cited at the bottom
- Confidence score and which agent answered

---

## 2️⃣ **Map View** - See Complaints on a Map

**URL**: http://localhost:3000/map

### What You Can Do:
- View all citizen complaints on an interactive map
- Filter complaints by type (Pothole, Water, Street Light, etc.)
- Filter by ward (Ward 1, Ward 2, Ward 3)
- Click on markers to see complaint details

### How to Use:
1. Click on the **"Map View"** green card on the homepage
2. The map loads automatically showing all complaints
3. Use the dropdowns at the top to filter:
   - **Type Filter**: Choose complaint type (All, Pothole, Water Supply, etc.)
   - **Ward Filter**: Choose ward (All, Ward 1, Ward 2, Ward 3)
4. Click on any marker (📍) to see details:
   - Complaint ID
   - Type
   - Status (Open/Resolved)
   - Description
   - Date reported

### What You'll See:
- Interactive map with complaint markers
- Statistics panel on the right showing:
  - Total complaints
  - Open vs Resolved count
  - Breakdown by type
  - Breakdown by ward

---

## 3️⃣ **Documents** - Upload Policy Files

**URL**: http://localhost:3000/documents

### What You Can Do:
- Upload new policy documents (PDF, Word, TXT)
- Add documents to the AI's knowledge base
- Make documents searchable via chat

### How to Use:
1. Click on the **"Documents"** purple card on the homepage
2. Click **"Choose File"** button or drag & drop a file
3. Supported formats: PDF, DOCX, TXT
4. Fill in optional metadata:
   - **Document Type**: Policy, SOP, Report, etc.
   - **Category**: Water, Roads, etc.
   - **Tags**: Keywords (comma-separated)
5. Click **"Upload Document"**
6. Wait for upload to complete

### What Happens:
- Document is processed and split into chunks
- Content is embedded into vectors
- Stored in the knowledge base
- Now searchable via AI Chat

### Already Uploaded Documents:
✅ Water Supply SOP (water-supply-sop.txt)
✅ Road Maintenance SOP (road-maintenance-sop.txt)

---

## 4️⃣ **Dashboard** - View System Statistics

**URL**: http://localhost:3000/dashboard

### What You Can Do:
- Monitor system health
- View usage statistics
- Check how many documents are loaded
- See total queries processed

### What You'll See:
- **System Status**: Online/Offline indicator
- **Total Queries**: Number of questions asked
- **Documents Count**: Total documents in knowledge base
- **Active Agents**: Which AI agents are running
- **Uptime**: How long the system has been running

### How to Use:
1. Click on the **"Dashboard"** orange card on the homepage
2. View all statistics at a glance
3. Page auto-refreshes every 30 seconds

---

## 🎓 Beginner's Walkthrough

### **First Time? Do This:**

#### **Step 1: Test the Chat (2 minutes)**
1. Go to http://localhost:3000/chat
2. Type: `"What are the water quality standards?"`
3. Press Enter
4. Read the AI's response - it should mention WHO standards, pH testing, etc.

#### **Step 2: View the Map (1 minute)**
1. Go to http://localhost:3000/map
2. Look at the markers on the map
3. Click on any marker to see complaint details
4. Try filtering by "Pothole" in the Type dropdown

#### **Step 3: Check the Dashboard (1 minute)**
1. Go to http://localhost:3000/dashboard
2. See how many documents are loaded
3. Check system status

#### **Step 4: Upload a Document (3 minutes)**
1. Create a simple text file on your desktop called `test-policy.txt`
2. Add some content like:
   ```
   Test Policy Document
   
   This is a test policy for waste management.
   All waste should be collected daily.
   Recycling bins should be emptied weekly.
   ```
3. Go to http://localhost:3000/documents
4. Click "Choose File" and select your test-policy.txt
5. Click "Upload Document"
6. Wait for success message

#### **Step 5: Query Your Document (1 minute)**
1. Go back to http://localhost:3000/chat
2. Ask: `"How often should recycling bins be emptied?"`
3. The AI should respond with: "Weekly" based on your uploaded document

---

## 💡 Pro Tips

### Getting Better Answers:
- ✅ **Be specific**: Instead of "water", ask "What are the water quality testing requirements?"
- ✅ **Ask one thing**: Don't ask multiple questions at once
- ✅ **Use proper names**: Refer to documents, wards, or complaint types by name

### Map View Tips:
- 🗺️ Use filters to narrow down results
- 🗺️ Click markers to see full complaint details
- 🗺️ Stats panel updates when you filter

### Document Upload Tips:
- 📄 Smaller files upload faster
- 📄 Add metadata to make documents easier to find later
- 📄 Use descriptive filenames

---

## ❓ Common Questions

**Q: Why isn't the AI answering my question?**
- A: It can only answer based on uploaded documents. If there's no relevant document, it will say so.

**Q: Can I upload PDFs?**
- A: Yes! PDF, DOCX, and TXT files are all supported.

**Q: How do I delete a document?**
- A: Currently, you need to use the API at http://localhost:8000/docs

**Q: The map isn't loading?**
- A: Make sure the backend is running at http://localhost:8000

**Q: Can I use my own OpenAI API key?**
- A: Yes! Edit the `.env` file and set `OPENAI_API_KEY=your-key-here` and `USE_MOCK_LLM=false`

---

## 🚀 What to Do Right Now

**Recommended First Actions:**

1. **Try the Chat** → http://localhost:3000/chat
   - Ask: "What are the water quality standards?"
   
2. **View the Map** → http://localhost:3000/map
   - Click on some complaint markers
   
3. **Check Stats** → http://localhost:3000/dashboard
   - See your system status

---

## 🆘 Need Help?

- **API Documentation**: http://localhost:8000/docs (Advanced users)
- **System Health**: http://localhost:8000/health
- **Backend Status**: http://localhost:8000/status

---

## 📱 Page Navigation

From any page, you can:
- Click the **home icon** (top left) to return to the homepage
- Use browser back button to go back
- Bookmark frequently used pages

---

**That's it! You're ready to use your Smart City AI Assistant!** 🎉

Start with the Chat page and ask some questions!
