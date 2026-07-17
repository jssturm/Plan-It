# iPhone 17 — Plan-It Shortcut Setup

**Server URL:** `http://192.168.4.88:8000/start-day`  
**Requirement:** iPhone and Windows PC on the same Wi-Fi network

---

## Step-by-Step

### Step 1: Open Shortcuts
Launch the **Shortcuts** app (pre-installed on all iPhones).  
If you can't find it, swipe down on the home screen and type "Shortcuts."

### Step 2: Create a New Shortcut
Tap the **+** button in the top right corner.

### Step 3: Add the API Call
1. Tap **Add Action**
2. Search: **"Get Contents of URL"**
3. Tap the result (icon: globe with URL)
4. Configure it:
   - **Method:** tap `GET` → change to **`POST`**
   - **URL:** tap and type: `http://192.168.4.88:8000/start-day`
5. Tap **Show More** (the little chevron arrow below the URL)
   - Tap **Headers** → tap **"Add new header"**
     - Key: `Content-Type`
     - Value: `application/json`
   - Tap **Request Body** → select **JSON** (instead of Form)
     - Tap **"Add new field"**
       - Key: `input`
       - Text: tap the value area, then tap **"Ask Each Time"** from the suggestion bar above the keyboard

### Step 4: Debug — Confirm the response shape (IMPORTANT)
1. Tap the gray **+** button (below your first action)
2. Search: **"Quick Look"** and tap it
3. Tap its input area → select **"Contents of URL"** from the variable picker
4. **Run the shortcut once.** You should see a flat JSON object with keys like:
   ```
   next_map_url, departure_time, schedule, alerts, actions
   ```
   If you see `choices` or `id` at the top level, the backend is broken — stop and fix the server.
5. **After confirming**, tap and hold the Quick Look action and delete it (debug only).

### Step 5: Parse the JSON Response
1. Tap **+**
2. Search: **"Get Dictionary from Input"** and tap it
3. Tap the blue **"Input"** text → a variable picker slides up
4. Select **"Contents of URL"** from the list

### Step 6: Extract the Map URL
1. Tap **+**
2. Search: **"Get Value from Dictionary"** and tap it
3. Tap the light-blue **"Dictionary"** bubble → select **"Dictionary"** (from Step 5)
4. Tap the **"Key"** field → a type picker appears
5. Select **"Text"** → type `next_map_url` → tap Done

### Step 7: Store the URL in a Variable (THIS IS CRITICAL)
1. Tap **+**
2. Search: **"Set Variable"** and tap it
3. Tap the **"Variable Name"** field → type: `MapURL`
4. The input field auto-populates with the result of Step 6. If not, tap it and select **"Dictionary Value"**

### Step 8: Auto-Open Google Maps
1. Tap **+**
2. Search: **"Open URLs"** and tap it
3. Tap the URL field → a variable picker slides up
4. Select **"MapURL"** (the variable you created in Step 7)

### Step 9: Show Itinerary
1. Tap **+**
2. Search: **"Show Result"** and tap it
3. Tap the text area → select **"Dictionary"** (from Step 5)

### Step 10: Name & Test
1. Tap the shortcut title at the top of the screen → **Rename**
2. Type: **Plan-It**
3. Tap **Done**
4. **Test it now.** Tap the shortcut. When prompted, type something like:
   ```
   Trip to Kennedy Space Center tomorrow morning with lunch stop
   ```
   Tap **Done**. If asked for network permission, tap **Allow**.  
   Google Maps opens to your first stop, and your itinerary appears on screen.

### Step 11: Voice Trigger with Siri
Just say: **"Hey Siri, Plan-It"**  
Siri runs the shortcut and prompts for trip details. Speak what you want.

---

## Action Summary (Production Flow)

```
1. Get Contents of URL       → POST http://192.168.4.88:8000/start-day
                                  Headers: Content-Type = application/json
                                  Body (JSON): {"input": Ask Each Time}
2. [DEBUG] Quick Look        → Contents of URL (delete after confirming shape)
3. Get Dictionary from Input → from "Contents of URL"
4. Get Value from Dictionary → key: next_map_url (type: Text)
5. Set Variable              → name: MapURL, value: Dictionary Value
6. Open URLs                 → MapURL (the variable)
7. Show Result               → Dictionary
```

## Response Shape (what the API returns)

```json
{
  "next_map_url": "https://www.google.com/maps/dir/?api=1&destination=...",
  "departure_time": "07:30 AM",
  "schedule": [
    "07:30 AM — Depart for Disney World",
    "09:00 AM — Arrive at Disney World",
    ...
  ],
  "alerts": ["Traffic warning", "Weather note"],
  "actions": [
    {"type": "open_maps", "url": "https://..."}
  ]
}
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Could not connect" | Make sure the server is running on your PC |
| "Network error" | Confirm iPhone and PC are on same Wi-Fi |
| "Dict has no value for key" | Run Quick Look debug (Step 4) to confirm `next_map_url` is present |
| IP changed | Run `ipconfig` in PowerShell, find your Wi-Fi IPv4, update URL in Step 3 |
| Server not running | `cd ~/development/jeffos && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000` |