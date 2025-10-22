# 🚀 Quick Start Guide - Travel Agent System

## 🎯 **Current Status**
- ✅ **Frontend Server**: Running on http://localhost:3000
- ✅ **Backend Server**: Running on http://localhost:8000
- ✅ **Dependencies**: Installed
- ⚠️ **Issue**: Frontend still using old city recognition

## 🚀 **How to Run the System**

### **Option 1: Use the Startup Script (Recommended)**
```bash
./start_system.sh
```

### **Option 2: Manual Startup**

#### **Step 1: Start Backend (Terminal 1)**
```bash
cd backend
python -m uvicorn main_async:app --host 0.0.0.0 --port 8000 --reload
```

#### **Step 2: Start Frontend (Terminal 2)**
```bash
npm start
```

#### **Step 3: Open Chat Interface**
- Open `index.html` in your browser
- Or visit: http://localhost:3000 (if serving HTML)

## 🧪 **Testing the System**

### **Test 1: Backend City API**
```bash
curl -X POST http://localhost:8000/api/cities/match \
  -H "Content-Type: application/json" \
  -d '{"input": "coimbatore"}'
```

### **Test 2: Frontend Chat API**
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "coimbatore to bangalore next week", "context": {"step": "initial"}}'
```

### **Test 3: Full Integration**
```bash
# Test Coimbatore recognition
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "coimbatore", "context": {"step": "collecting"}}'
```

## 🔧 **Current Issue & Solution**

### **Problem:**
The frontend is still using the old city recognition logic instead of calling the backend API.

### **Solution:**
The frontend needs to be updated to use the backend city API. The backend is working perfectly, but the frontend integration needs to be completed.

### **Quick Fix:**
1. **Backend is working**: ✅ Coimbatore is recognized
2. **Frontend needs update**: ⚠️ Still using old logic
3. **Integration needed**: 🔧 Connect frontend to backend

## 📊 **System Status**

| Component | Status | Port | Notes |
|-----------|--------|------|-------|
| **Backend API** | ✅ Running | 8000 | City recognition working |
| **Frontend Server** | ✅ Running | 3000 | Chat interface ready |
| **City API** | ✅ Working | 8000 | Coimbatore recognized |
| **Integration** | ⚠️ Partial | - | Frontend needs update |

## 🎯 **Next Steps**

1. **Test Backend**: Verify city recognition works
2. **Update Frontend**: Connect to backend API
3. **Test Integration**: Verify full system works
4. **Open Chat UI**: Use the web interface

## 🌐 **Access Points**

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Chat UI**: Open `index.html` in browser
- **API Docs**: http://localhost:8000/docs

## 🛑 **Stopping the System**

Press `Ctrl+C` in each terminal to stop the servers.

---

**The system is ready to run! The backend city recognition is working perfectly. The frontend just needs to be connected to use the backend API.**
