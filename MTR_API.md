# Comprehensive Guide to MTR Next Train API

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [API Fundamentals](#api-fundamentals)
4. [Parameters Explained](#parameters-explained)
5. [Response Formats](#response-formats)
6. [Common Use Cases](#common-use-cases)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Code Examples](#code-examples)

---

## Overview

The **MTR Next Train API** is a REST-based service provided by the Hong Kong MTR Corporation that delivers real-time train arrival schedules across multiple MTR lines. This API enables developers to build applications that display upcoming train arrivals for passengers planning their journeys.

### Supported Lines

The API covers all major MTR lines in Hong Kong:
- **Airport Express Line (AEL)** - 5 stations
- **Tung Chung Line (TCL)** - 8 stations
- **Tuen Ma Line (TML)** - 20 stations
- **Tseung Kwan O Line (TKL)** - 8 stations
- **East Rail Line (EAL)** - 16 stations
- **South Island Line (SIL)** - 5 stations
- **Tsuen Wan Line (TWL)** - 15 stations
- **Island Line (ISL)** - 17 stations
- **Kwun Tong Line (KTL)** - 15 stations
- **Disneyland Resort Line (DRL)** - 2 stations

---

## Getting Started

### Basic Requirements

- **Access Method:** HTTP GET requests
- **Base URL:** `https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php`
- **Response Format:** JSON
- **Authentication:** None required (public API)
- **Rate Limiting:** 429 status code indicates too many requests

### Quick Start Example

```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=TKO
```

This request retrieves the next train schedules for Tseung Kwan O (TKO) station on the Tseung Kwan O Line (TKL).

---

## API Fundamentals

### Request Structure

All API requests follow this pattern:

```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=[LINE_CODE]&sta=[STATION_CODE]&lang=[LANGUAGE]
```

### Request Method
- **Type:** REST
- **HTTP Method:** GET
- **Content-Type:** Not required (parameters passed via URL)

### Response Type
- **Format:** JSON
- **Character Encoding:** UTF-8
- **Typical Response Time:** < 1 second

---

## Parameters Explained

### Parameter 1: Line Code (Required)

Specifies which MTR line to query. Must be combined with a valid station code on that line.

| Line Code | Line Name | Stations |
|---|---|---|
| **AEL** | Airport Express | 5 |
| **TCL** | Tung Chung Line | 8 |
| **TML** | Tuen Ma Line | 20 |
| **TKL** | Tseung Kwan O Line | 8 |
| **EAL** | East Rail Line | 16 |
| **SIL** | South Island Line | 5 |
| **TWL** | Tsuen Wan Line | 15 |
| **ISL** | Island Line | 17 |
| **KTL** | Kwun Tong Line | 15 |
| **DRL** | Disneyland Resort Line | 2 |

### Parameter 2: Station Code (Required)

Specifies the station on the selected line. Each line has its own set of valid station codes.

#### Airport Express Line (AEL) Stations
- **HOK** - Hong Kong
- **KOW** - Kowloon
- **TSY** - Tsing Yi
- **AIR** - Airport
- **AWE** - AsiaWorld Expo

#### Tung Chung Line (TCL) Stations
- **HOK** - Hong Kong
- **KOW** - Kowloon
- **OLY** - Olympic
- **NAC** - Nam Cheong
- **LAK** - Lai King
- **TSY** - Tsing Yi
- **SUN** - Sunny Bay
- **TUC** - Tung Chung

#### Tuen Ma Line (TML) Stations
- **WKS** - Wu Kai Sha
- **MOS** - Ma On Shan
- **HEO** - Heng On
- **TSH** - Tai Shui Hang
- **SHM** - Shek Mun
- **CIO** - City One
- **STW** - Sha Tin Wai
- **CKT** - Che Kung Temple
- **TAW** - Tai Wai
- **HIK** - Hin Keng
- **DIH** - Diamond Hill
- **KAT** - Kai Tak
- **SUW** - Sung Wong Toi
- **TKW** - To Kwan Wan
- **HOM** - Ho Man Tin
- **HUH** - Hung Hom
- **ETS** - East Tsim Sha Tsui
- **AUS** - Austin
- **NAC** - Nam Cheong
- **MEF** - Mei Foo
- **TWW** - Tsuen Wan West
- **KSR** - Kam Sheung Road
- **YUL** - Yuen Long
- **LOP** - Long Ping
- **TIS** - Tin Shui Wai
- **SIH** - Siu Hong
- **TUM** - Tuen Mun

#### Tseung Kwan O Line (TKL) Stations
- **NOP** - North Point
- **QUB** - Quarry Bay
- **YAT** - Yau Tong
- **TIK** - Tiu Keng Leng
- **TKO** - Tseung Kwan O
- **LHP** - LOHAS Park
- **HAH** - Hang Hau
- **POA** - Po Lam

#### East Rail Line (EAL) Stations
- **ADM** - Admiralty
- **EXC** - Exhibition Centre
- **HUH** - Hung Hom
- **MKK** - Mong Kok East
- **KOT** - Kowloon Tong
- **TAW** - Tai Wai
- **SHT** - Sha Tin
- **FOT** - Fo Tan
- **RAC** - Racecourse
- **UNI** - University
- **TAP** - Tai Po Market
- **TWO** - Tai Wo
- **FAN** - Fanling
- **SHS** - Sheung Shui
- **LOW** - Lo Wu
- **LMC** - Lok Ma Chau

#### South Island Line (SIL) Stations
- **ADM** - Admiralty
- **OCP** - Ocean Park
- **WCH** - Wong Chuk Hang
- **LET** - Lei Tung
- **SOH** - South Horizons

#### Tsuen Wan Line (TWL) Stations
- **CEN** - Central
- **ADM** - Admiralty
- **TST** - Tsim Sha Tsui
- **JOR** - Jordan
- **YMT** - Yau Ma Tei
- **MOK** - Mong Kok
- **PRE** - Price Edward
- **SSP** - Sham Shui Po
- **CSW** - Cheung Sha Wan
- **LCK** - Lai Chi Kok
- **MEF** - Mei Foo
- **LAK** - Lai King
- **KWF** - Kwai Fong
- **KWH** - Kwai Hing
- **TWH** - Tai Wo Hau
- **TSW** - Tsuen Wan

#### Island Line (ISL) Stations
- **KET** - Kennedy Town
- **HKU** - HKU
- **SYP** - Sai Ying Pun
- **SHW** - Sheung Wan
- **CEN** - Central
- **ADM** - Admiralty
- **WAC** - Wan Chai
- **CAB** - Causeway Bay
- **TIH** - Tin Hau
- **FOH** - Fortress Hill
- **NOP** - North Point
- **QUB** - Quarry Bay
- **TAK** - Tai Koo
- **SWH** - Sai Wan Ho
- **SKW** - Shau Kei Wan
- **HFC** - Heng Fa Chuen
- **CHW** - Chai Wan

#### Kwun Tong Line (KTL) Stations
- **WHA** - Whampoa
- **HOM** - Ho Man Tin
- **YMT** - Yau Ma Tei
- **MOK** - Mong Kok
- **PRE** - Prince Edward
- **SKM** - Shek Kip Mei
- **KOT** - Kowloon Tong
- **LOF** - Lok Fu
- **WTS** - Wong Tai Sin
- **DIH** - Diamond Hill
- **CHH** - Choi Hung
- **KOB** - Kowloon Bay
- **NTK** - Ngau Tau Kok
- **KWT** - Kwun Tong
- **LAT** - Lam Tin
- **YAT** - Yau Tong
- **TIK** - Tiu Keng Leng

#### Disneyland Resort Line (DRL) Stations
- **SUN** - Sunny Bay
- **DIS** - Disneyland Resort

### Parameter 3: Language (Optional)

Specifies the language of the returned result. Defaults to English if not specified.

| Language Code | Language |
|---|---|
| **EN** | English (Default) |
| **TC** | Traditional Chinese |

**Example:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=TKO&lang=TC
```

---

## Response Formats

### Success Response Structure

```json
{
  "sys_time": "2022-04-25 15:19:59",
  "curr_time": "2022-04-25 15:19:59",
  "data": {
    "TKL-TKO": {
      "curr_time": "2022-04-25 15:19:59",
      "sys_time": "2022-04-25 15:19:59",
      "UP": [
        {
          "ttnt": "1",
          "valid": "Y",
          "plat": "1",
          "time": "2022-04-25 15:20:00",
          "source": "-",
          "dest": "POA",
          "seq": "1"
        }
      ],
      "DOWN": [
        {
          "ttnt": "2",
          "valid": "Y",
          "plat": "2",
          "time": "2022-04-25 15:21:00",
          "source": "-",
          "dest": "NOP",
          "seq": "1"
        }
      ]
    }
  },
  "status": 1,
  "message": "successful",
  "isdelay": "N"
}
```

### Response Field Explanations

| Field | Type | Description |
|---|---|---|
| **sys_time** | String (DateTime) | System time when the request was processed (YYYY-MM-DD HH:MM:SS) |
| **curr_time** | String (DateTime) | Current time according to the system |
| **data** | Object | Contains the train schedule information organized by line-station combination |
| **status** | Integer | Response status: 1 = successful, 0 = special message or alert |
| **message** | String | Status message, either "successful" or descriptive alert |
| **isdelay** | String | Indicates if there is service delay: "Y" = delay, "N" = no delay |

### Train Entry Fields

| Field | Type | Example | Description |
|---|---|---|---|
| **ttnt** | String | "1" | Time to next train in minutes |
| **valid** | String | "Y" | Validity of data: "Y" = valid, "N" = invalid |
| **plat** | String | "1" | Platform number |
| **time** | String | "2022-04-25 15:20:00" | Scheduled arrival time (YYYY-MM-DD HH:MM:SS) |
| **source** | String | "-" | Train source (typically "-" for regular service) |
| **dest** | String | "POA" | Destination station code |
| **seq** | String | "1" | Sequence number of train in the upcoming list |

### HTTP Status Codes

| HTTP Code | Meaning | Description |
|---|---|---|
| **200** | Success | Request processed successfully |
| **429** | Too Many Requests | Rate limit exceeded; wait before retrying |
| **500** | Internal Server Error | Server encountered an error; retry later |

---

## Common Use Cases

### Use Case 1: Display Next Arriving Train

**Scenario:** A commuter app needs to show the time until the next train arrives at Central Station on the Island Line.

**Request:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=ISL&sta=CEN
```

**Processing:**
1. Extract the first entry from the "UP" array (upbound trains)
2. Display the `ttnt` value (time to next train) to the user
3. Show the destination (`dest`) and scheduled time (`time`)

**Display Example:**
```
Next Train (Towards Chai Wan): 3 minutes
Arrival: 15:23
Platform: 2
```

### Use Case 2: Multi-Language Support

**Scenario:** Support both English and Traditional Chinese speakers.

**English Request:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=TKO&lang=EN
```

**Traditional Chinese Request:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=TKO&lang=TC
```

### Use Case 3: Handle Service Disruptions

**Scenario:** A station is suspended due to service disruption.

**Request:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=EAL&sta=LOW
```

**Response:**
```json
{
  "status": 0,
  "message": "LOW station is suspended"
}
```

**Application Action:** Display warning message to users; recommend alternative routes.

### Use Case 4: Check for Service Announcements

**Scenario:** Special train service arrangements are in effect.

**Request:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=TKO&lang=en
```

**Response:**
```json
{
  "status": 0,
  "message": "Special train service arrangements are now in place on this line. Please click here for more information.",
  "url": "https://www.mtr.com.hk/alert/alert_title_wap.html",
  "cur_time": "2019-06-13 17:34:58"
}
```

**Application Action:** Display alert banner with link to more information.

### Use Case 5: Determine If Last Train Has Passed

**Scenario:** Check if the last train on a line has already left the station.

**Request:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=TKL&sta=TKO
```

**Response Indicators:**
- If `DOWN` array is empty and `UP` array has only one entry → Last train is imminent
- If both arrays are empty → Service has ended for the day

### Use Case 6: Handle Data Absence

**Scenario:** Data is temporarily unavailable due to system delay.

**Response:**
```json
{
  "sys_time": "-",
  "curr_time": "-",
  "data": {
    "TKL-TKO": {
      "curr_time": "-",
      "sys_time": "-"
    }
  },
  "status": 1,
  "message": "successful",
  "isdelay": "Y"
}
```

**Application Action:** Display loading message; retry the request after a short delay.

---

## Error Handling

### Common Error Scenarios

#### 1. Invalid Parameter Combination

**Cause:** Station code doesn't belong to the specified line.

**Example:**
```
https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=AEL&sta=TKO
```

**Result:** Empty or error response. Always validate parameter combinations.

#### 2. Rate Limiting

**HTTP 429 Response**

```
Too Many Requests - The API has received too many requests in a short time.
```

**Solution:**
- Implement exponential backoff retry logic
- Cache responses for 10-30 seconds
- Distribute requests across time instead of making simultaneous calls

#### 3. Network Timeout

**Cause:** API server is unresponsive or network connection is lost.

**Solution:**
- Set a timeout of 10-15 seconds per request
- Implement retry logic with exponential backoff (wait 1s, 2s, 4s, etc.)
- Display cached data if available while retrying

#### 4. Invalid Station Code

**Cause:** Typo in station code or non-existent station.

**Solution:**
- Validate station codes against known valid codes
- Provide autocomplete dropdown for station selection
- Display error message with list of valid stations

#### 5. Service Suspended

**Response:**
```json
{
  "status": 0,
  "message": "XXX station is suspended"
}
```

**Solution:**
- Check the message field for suspension notices
- Inform users about the disruption
- Provide alternative route suggestions

### Recommended Error Handling Flow

```
Request API
    ↓
Check HTTP Status Code
    ├─ 200 → Parse JSON response
    ├─ 429 → Wait and retry with backoff
    ├─ 500 → Show cached data, retry after delay
    └─ Other → Show error message
    ↓
Parse JSON Response
    ├─ status == 0 → Check message (alert or suspension)
    ├─ status == 1 → Extract train data
    ├─ isdelay == "Y" → Show delay notice
    └─ Empty data → Show no trains available
    ↓
Display to User
```

---

## Best Practices

### 1. Caching Strategy

**Implement intelligent caching:**

```
- Cache successful responses for 15-30 seconds
- Cache "last train" responses for 5 minutes
- Cache station suspension notices for 1 hour
- Do not cache special service announcements (update frequently)
```

**Benefits:**
- Reduces server load
- Improves app performance
- Provides better user experience during network issues

### 2. Request Frequency

**Recommended polling intervals:**

```
- Active user viewing train times: 10-15 seconds
- Background refresh: 30-60 seconds
- Idle app: Do not poll (wait for user action)
- During peak hours: 20-30 seconds (reduce load)
```

### 3. Parameter Validation

**Always validate before making requests:**

```javascript
function validateParameters(line, station) {
  const validLines = ['AEL', 'TCL', 'TML', 'TKL', 'EAL', 'SIL', 'TWL', 'ISL', 'KTL', 'DRL'];
  const validStations = {
    'AEL': ['HOK', 'KOW', 'TSY', 'AIR', 'AWE'],
    'TKL': ['NOP', 'QUB', 'YAT', 'TIK', 'TKO', 'LHP', 'HAH', 'POA'],
    // ... more lines
  };
  
  if (!validLines.includes(line)) throw new Error('Invalid line code');
  if (!validStations[line].includes(station)) throw new Error('Invalid station for line');
  
  return true;
}
```

### 4. Graceful Degradation

**Handle various response scenarios:**

```
Scenario 1: Normal operation → Show all upcoming trains
Scenario 2: Data delay (isdelay="Y") → Show cached data + "Data may be delayed" notice
Scenario 3: Service suspension → Show "Service suspended" message
Scenario 4: Special arrangements → Show alert banner + link to details
Scenario 5: Last trains → Highlight that few trains remain
Scenario 6: Network error → Show last known data or "Retrying..."
```

### 5. User-Friendly Display

**Present data clearly:**

```
✓ Show time to next train prominently
✓ Indicate destination clearly
✓ Show platform number
✓ Use intuitive platform/direction icons
✓ Display countdown timer (updated every 10 seconds)
✓ Highlight alerts and service notices
✓ Show "Last train" warning
```

### 6. Timezone Handling

**Important considerations:**

```
- API returns times in Hong Kong time (HKT, UTC+8)
- Convert to local timezone if user is in different location
- Always store timestamps in UTC internally
- Display in HKT for users in Hong Kong
```

### 7. Accessibility

**Ensure app is usable by everyone:**

```
- Provide text alternatives for visual indicators
- Use clear, large fonts for times
- Support screen readers
- Provide haptic feedback for alerts
- Support high contrast mode
```

### 8. Testing

**Test these scenarios:**

```
✓ Valid line and station combination
✓ Invalid line code
✓ Invalid station for the line
✓ Station suspension
✓ Special service arrangements
✓ Last train scenarios
✓ No trains available
✓ Data absence/delay
✓ Network timeout
✓ Rate limiting (429 response)
✓ Server error (500 response)
✓ Multiple language requests
✓ Rapid successive requests
✓ App backgrounded and resumed
```

---

## Code Examples

### Example 1: JavaScript/Node.js

```javascript
async function getNextTrain(line, station, language = 'EN') {
  const baseURL = 'https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php';
  const params = new URLSearchParams({
    line: line.toUpperCase(),
    sta: station.toUpperCase(),
    lang: language.toUpperCase()
  });
  
  try {
    const response = await fetch(`${baseURL}?${params}`, {
      method: 'GET',
      timeout: 10000
    });
    
    if (!response.ok) {
      if (response.status === 429) {
        console.log('Rate limited. Retry after delay.');
        return null;
      }
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    // Handle special cases
    if (data.status === 0) {
      console.log(`Alert: ${data.message}`);
      return { alert: data.message, url: data.url };
    }
    
    if (data.isdelay === 'Y') {
      console.log('Data may be delayed');
    }
    
    // Extract next train info
    const stationKey = `${line.toUpperCase()}-${station.toUpperCase()}`;
    const stationData = data.data[stationKey];
    
    if (!stationData || !stationData.UP || stationData.UP.length === 0) {
      return { message: 'No trains available' };
    }
    
    const nextTrain = stationData.UP[0];
    return {
      minutesToArrival: nextTrain.ttnt,
      destination: nextTrain.dest,
      arrivalTime: nextTrain.time,
      platform: nextTrain.plat,
      valid: nextTrain.valid === 'Y'
    };
    
  } catch (error) {
    console.error('Error fetching train data:', error);
    return null;
  }
}

// Usage
const train = await getNextTrain('TKL', 'TKO');
if (train) {
  console.log(`Next train in ${train.minutesToArrival} minutes to ${train.destination}`);
}
```

### Example 2: Python

```python
import requests
import json
from datetime import datetime
from typing import Dict, Optional

class MTRNextTrainAPI:
    BASE_URL = 'https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php'
    TIMEOUT = 10
    
    VALID_LINES = ['AEL', 'TCL', 'TML', 'TKL', 'EAL', 'SIL', 'TWL', 'ISL', 'KTL', 'DRL']
    
    VALID_STATIONS = {
        'AEL': ['HOK', 'KOW', 'TSY', 'AIR', 'AWE'],
        'TKL': ['NOP', 'QUB', 'YAT', 'TIK', 'TKO', 'LHP', 'HAH', 'POA'],
        # ... add all other lines
    }
    
    @staticmethod
    def validate_parameters(line: str, station: str) -> bool:
        """Validate line and station combination."""
        if line.upper() not in MTRNextTrainAPI.VALID_LINES:
            raise ValueError(f"Invalid line: {line}")
        
        if line.upper() not in MTRNextTrainAPI.VALID_STATIONS:
            raise ValueError(f"No station data for line: {line}")
        
        if station.upper() not in MTRNextTrainAPI.VALID_STATIONS[line.upper()]:
            raise ValueError(f"Invalid station {station} for line {line}")
        
        return True
    
    @staticmethod
    def get_next_train(line: str, station: str, language: str = 'EN') -> Optional[Dict]:
        """Fetch next train information."""
        try:
            MTRNextTrainAPI.validate_parameters(line, station)
            
            params = {
                'line': line.upper(),
                'sta': station.upper(),
                'lang': language.upper()
            }
            
            response = requests.get(
                MTRNextTrainAPI.BASE_URL,
                params=params,
                timeout=MTRNextTrainAPI.TIMEOUT
            )
            
            if response.status_code == 429:
                print("Rate limited. Please retry after delay.")
                return None
            
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return None
            
            data = response.json()
            
            # Handle alerts
            if data.get('status') == 0:
                return {
                    'alert': data.get('message'),
                    'url': data.get('url'),
                    'type': 'alert'
                }
            
            # Check for delay
            if data.get('isdelay') == 'Y':
                print("Warning: Data may be delayed")
            
            # Extract train data
            station_key = f"{line.upper()}-{station.upper()}"
            station_data = data.get('data', {}).get(station_key)
            
            if not station_data or not station_data.get('UP'):
                return {'message': 'No trains available', 'type': 'no_trains'}
            
            next_train = station_data['UP'][0]
            
            return {
                'type': 'success',
                'minutes_to_arrival': int(next_train['ttnt']),
                'destination': next_train['dest'],
                'arrival_time': next_train['time'],
                'platform': next_train['plat'],
                'valid': next_train['valid'] == 'Y',
                'system_time': data.get('sys_time'),
                'is_delayed': data.get('isdelay') == 'Y'
            }
            
        except requests.exceptions.Timeout:
            print("Request timeout")
            return None
        except ValueError as e:
            print(f"Validation error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

# Usage
api = MTRNextTrainAPI()
result = api.get_next_train('TKL', 'TKO', 'EN')
if result and result.get('type') == 'success':
    print(f"Next train in {result['minutes_to_arrival']} minutes to {result['destination']}")
    print(f"Arrives at: {result['arrival_time']}")
    print(f"Platform: {result['platform']}")
```

### Example 3: React Component

```jsx
import React, { useState, useEffect } from 'react';

const NextTrainDisplay = ({ line, station }) => {
  const [train, setTrain] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [countdown, setCountdown] = useState(0);
  
  const BASE_URL = 'https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php';
  const REFRESH_INTERVAL = 15000; // 15 seconds
  
  useEffect(() => {
    fetchTrainData();
    const interval = setInterval(fetchTrainData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [line, station]);
  
  useEffect(() => {
    if (train && train.minutesToArrival) {
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev > 0) return prev - 1;
          return 0;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [train]);
  
  const fetchTrainData = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${BASE_URL}?line=${line}&sta=${station}&lang=EN`
      );
      
      if (response.status === 429) {
        setError('Service temporarily busy. Retrying...');
        return;
      }
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      
      if (data.status === 0) {
        setError(data.message);
        setTrain(null);
        return;
      }
      
      const stationKey = `${line.toUpperCase()}-${station.toUpperCase()}`;
      const stationData = data.data[stationKey];
      
      if (!stationData?.UP?.[0]) {
        setError('No trains available');
        return;
      }
      
      const nextTrain = stationData.UP[0];
      setTrain({
        minutesToArrival: parseInt(nextTrain.ttnt),
        destination: nextTrain.dest,
        arrivalTime: nextTrain.time,
        platform: nextTrain.plat,
        isDelayed: data.isdelay === 'Y'
      });
      
      setCountdown(parseInt(nextTrain.ttnt) * 60);
      setError(null);
      
    } catch (err) {
      setError('Unable to fetch train data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const formatCountdown = () => {
    const minutes = Math.floor(countdown / 60);
    const seconds = countdown % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };
  
  if (loading && !train) return <div>Loading...</div>;
  
  if (error && !train) return <div className="error">{error}</div>;
  
  return (
    <div className="next-train-container">
      {train.isDelayed && (
        <div className="delay-warning">⚠️ Service delay in effect</div>
      )}
      
      <div className="train-info">
        <div className="time-display">
          <span className="minutes">{train.minutesToArrival}</span>
          <span className="label">minutes</span>
        </div>
        
        <div className="train-details">
          <div className="destination">
            Towards {train.destination}
          </div>
          <div className="arrival-time">
            Arrives: {train.arrivalTime}
          </div>
          <div className="platform">
            Platform {train.platform}
          </div>
        </div>
      </div>
      
      {error && <div className="error-note">{error}</div>}
    </div>
  );
};

export default NextTrainDisplay;
```

---

## Conclusion

The MTR Next Train API is a powerful tool for building Hong Kong transit applications. By following this guide and implementing the best practices outlined, you can create reliable, user-friendly applications that help commuters navigate the MTR system efficiently.

**Key Takeaways:**
- Always validate parameters before making requests
- Implement robust error handling and retry logic
- Cache responses intelligently to reduce server load
- Handle various response scenarios gracefully
- Provide clear, accessible user interfaces
- Test thoroughly across different scenarios
- Monitor rate limits and adjust polling frequency accordingly

For questions or issues, refer to the official MTR website or contact their support team.