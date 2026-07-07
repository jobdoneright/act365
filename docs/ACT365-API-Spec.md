# ACT365 API Specification

## Overview

**ACT365** (www.act365.eu) is the cloud-based access control system supported by Vanderbilt International. This API allows third-party developers to control customer access control systems and perform important activities including commanding doors, registering controllers, reviewing log events, viewing muster reports, creating/editing cardholders, and more.

This doc is a generated summary from the [official APIARY docs](https://act365api.docs.apiary.io/#).

### Service User Types

- **Installers**: Manage physical infrastructure including controllers, doors, and cameras
- **Customers**: End-users for the access control system

Access to the API is restricted to valid service user logins (defined within www.act365.eu only).

### Localization

- Set the `Accept-Language` HTTP header to the desired culture (e.g., `fr-FR`)
- Some API calls require location headers: `locationLatitude` and `locationLongitude`

---

## Authentication

### Get an Access Token

**Endpoint:** `POST https://userapi.act365.eu/api/account/login`

**Description:** Performs the login, which must be the first action taken.

**Request Format:** `application/x-www-form-urlencoded`

**Parameters:**
- `email` (string): Valid service user email
- `password` (string): Valid service user password

**Response:**
```json
{
  "access_token": "string",
  "token_type": "string",
  "expires_in": 86400,
  "userName": "string",
  ".issued": "datetime",
  ".expires": "datetime"
}
```

**Notes:**
- Valid access tokens last for **24 hours**
- Login API calls are limited to 1 per minute
- Must be the first API call made
- Token must be passed in `Authorization: Bearer {token}` header for all subsequent requests

---

## Throttling

Vanderbilt implements API throttling to ensure optimal service for all users.

**Throttling Behavior:**
- Excessive usage triggers HTTP 429 (Too Many Requests)
- Implemented on a per-user basis for 1 second/minute/hour/day/week time windows
- Usage monitoring is cumulative within each time window

**Response Headers:**
- `Retry-After`: Number of seconds to wait before retrying
- `Rate-Limit`: Active rate limit for the call
- `Rate-Period`: Time window type ("Second", "Minute", "Hour", "Day", "Week", "Concurrent")

---

## API Endpoints

### Summary Information

#### Get Quick Summary Information

**Endpoint:** `GET /api/summary`

**Description:** Lists customers and sites with ACU counts and muster information.

**Response:**
- For installers: Lists all customers and sites
- For customers: Returns only their own details
- Includes `mustered` cardholders (currently on the specified site)
- Returns `ServiceUserType` ("Installer" or "Customer")

---

### Customers

#### List All Customers

**Endpoint:** `GET /api/customers`

**Description:** Retrieves all customer details.

**Response:**
- For installers: Details on all available customers
- For customers: Only their own details
- Includes location coordinates with `LocationAccurate` flag
- Address and contact details may be empty or null

---

### Sites

#### List All Sites

**Endpoint:** `GET /api/sites`

**Query Parameters:**
- `customerid` (optional): Filter by specific customer

**Description:** Gets list of all available sites.

#### Get Site

**Endpoint:** `GET /api/sites/{siteid}`

**Parameters:**
- `siteid` (required): Site ID

**Description:** Returns information for a specific site.

---

### Site Lockdown

#### Lockdown Activate

**Endpoint:** `POST /api/lockdown/activate`

**Description:** Activates site lockdown (requires door group configuration).

#### Lockdown Clear

**Endpoint:** `POST /api/lockdown/clear`

**Description:** Clears site lockdown.

#### Lockdown Command

**Endpoint:** `POST /api/lockdown/command`

**Description:** Issues lockdown command to configured door group.

---

### Hardware: ACUs (Access Control Units)

#### List All ACUs

**Endpoint:** `GET /api/acus`

**Query Parameters:**
- `customerid` (optional): Filter by customer
- `siteid` (optional): Filter by site

**Description:** Gets all registered ACUs for the installer or customer.

#### Get ACU by Id

**Endpoint:** `GET /api/acus/{acuid}`

**Parameters:**
- `acuid` (required): Controller ID

**Description:** Returns individual ACU details.

#### Register ACU

**Endpoint:** `POST /api/acus`

**Request Body:**
```json
{
  "customerid": "integer",
  "siteid": "integer",
  "cuid": "string",
  "name": "string"
}
```

**Description:** Registers a new ACU (installers only).

**Notes:**
- CUID is the unique ID printed on the ACU
- A default door named "Door {ACU}" is created automatically
- ACU must be properly configured, powered, and internet-connected to come online

#### Delete ACU

**Endpoint:** `DELETE /api/acus/{acuid}`

**Parameters:**
- `acuid` (required): ACU ID

**Requires Location Headers:** May be required if customer requested additional security

**Description:** Unregisters an ACU and its associated doors.

**Notes:**
- Necessary before moving an ACU to another site

---

### Doors

#### List All Doors by Site or Customer

**Endpoint:** `GET /api/doors`

**Query Parameters:**
- `siteid` (optional): Filter by site
- `customerid` (optional): Filter by customer

**Description:** Gets list of doors (directly associated with ACUs).

**Field Prefixes:**
- "TZ" prefix refers to ACT timezones
- All time fields in seconds

**Door Operation Options (bit-mapped):**
- None = 0, OptLockSaver = 1, OptSilent = 2, OptChime = 4, OptFreeExit = 8, OptInterlock = 16, OptExitButton = 32, OptPinRequiredOnExit = 64, OptPir = 128, OptFailsafe = 256, OptToggle = 512, OptIntruderPanel = 1024, OptAccessOnly = 2048, OptBreakglass = 4096, OptTamper = 8192, OptMainsFault = 16384, OptContactMonitoring = 32768, OptUnlockFirstAccess = 65536, OptPinSearchAllCardholders = 131072

**Auxiliary Options (bit-mapped):**
- OptAuxActivateAjar = 1, OptAuxActivateForced = 2, OptAuxActivateOpen = 4, OptAuxActivateDenied = 8, OptAuxActivateGranted = 16, OptAuxActivateDuress = 32, OptAuxActivateExitGranted = 64, OptAuxActivateExitDenied = 128, OptAuxActivateFollowMainRelay = 256, OptAuxActivateArmIntruderPanel = 512, OptAuxActivateBreakglass = 1024

**Logging Options (bit-mapped):**
- OptLogForced = 1, OptLogReadErrors = 2, OptLogExitButton = 4, OptLogOpen = 8, OptLogClose = 16, OptLogDoorAjar = 32

#### Get Door

**Endpoint:** `GET /api/doors/{doorid}`

**Parameters:**
- `doorid` (required): Door ID

**Description:** Returns individual door details.

#### Get Doors for a Cardholder

**Endpoint:** `GET /api/doors/cardholder/{cardholderid}`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Description:** Returns the set of doors a cardholder can access.

#### Command a Single Door

**Endpoint:** `POST /api/doors/{doorid}/command`

**Parameters:**
- `doorid` (required): Door ID
- `command` (required): "Pass", "Normalise", "Lock", or "Unlock"

**Requires Location Headers:** May be required if customer requested additional security

**Description:** Issues a command to a door.

#### Command Set of Doors

**Endpoint:** `POST /api/doors/command`

**Request Body:**
```json
{
  "doors": ["integer"],
  "command": "string"
}
```

**Parameters:**
- `doors` (array): Array of door IDs
- `command` (string): "Pass", "Normalise", "Lock", or "Unlock"

**Requires Location Headers:** May be required if customer requested additional security

**Description:** Issues commands to multiple doors (only valid, enabled, and connected doors receive commands).

---

### Door Groups

#### Get Door Groups

**Endpoint:** `GET /api/doorgroups`

**Query Parameters:**
- `siteid` (optional): Filter by site
- `customerid` (optional): Filter by customer

**Description:** Gets door groups for a customer and/or site.

**Notes:**
- Every site has an "All Doors" door group (IsEditable=false)
- Every customer has "All Doors" for all sites (IsEditable=false)
- "No Doors" door group exists system-wide (IsEditable=false)

#### Get Door Group By Id

**Endpoint:** `GET /api/doorgroups/{doorgroupid}`

**Parameters:**
- `doorgroupid` (required): Door group ID

**Description:** Returns individual door group details (customers only).

#### Create Door Group

**Endpoint:** `POST /api/doorgroups`

**Request Body:**
```json
{
  "siteid": "integer",
  "customerid": "integer",
  "name": "string",
  "doors": ["integer"],
  "timezones": ["integer"]
}
```

**Description:** Adds new door group to the site.

**Notes:**
- Site and customer IDs are compulsory
- Doors list must be accessible for the site
- Empty doors list not accepted
- Returns new ID in response
- Wait 30 seconds before updating after creation

#### Update Door Group

**Endpoint:** `PUT /api/doorgroups/{doorgroupid}`

**Description:** Updates existing door group (all fields updated).

**Notes:**
- Wait 30 seconds before updating after creation

#### Delete Door Group

**Endpoint:** `DELETE /api/doorgroups/{doorgroupid}`

**Parameters:**
- `doorgroupid` (required): Door group ID

**Description:** Deletes door group (ID cannot be reused).

---

### Cameras

#### List All Cameras by Site or Door

**Endpoint:** `GET /api/cameras`

**Query Parameters:**
- `siteid` (optional): Filter by site
- `doorid` (optional): Filter by door

**Description:** Returns cameras available for viewing.

**Response:**
- `LiveFeed`: Contains HLS stream URL (Apple) and DASH stream URL (Android/Desktop)
- `DeviceStatus`: Indicates if camera is online or offline

---

### Reports

#### Muster Report

**Endpoint:** `GET /api/events/muster`

**Query Parameters:**
- `siteid` (required): Site ID

**Description:** Provides list of all cardholders currently on a customer's site.

#### Check Cardholder Out Manually

**Endpoint:** `POST /api/events/cardholder/{cardholderid}/checkout`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Requires Location Headers:** May be required if customer requested additional security

**Description:** Removes cardholder from muster report (when safely off-site).

#### Check Cardholder In Manually

**Endpoint:** `POST /api/events/cardholder/{cardholderid}/checkin`

**Parameters:**
- `cardholderid` (required): Cardholder ID
- `siteid` (required): Preferred site ID

**Requires Location Headers:** May be required if customer requested additional security

**Description:** Manually checks cardholder into specified site.

#### Log Event Report

**Endpoint:** `GET /api/events`

**Query Parameters:**
- `siteid` (required): Site ID

**Description:** Gets most recent log events for a site (shorter version).

**Notes:**
- Ordered by Time descending by default

#### Log Event Report for a Cardholder Group

**Endpoint:** `GET /api/events/cardholder-group/{cardholdergroup}`

**Parameters:**
- `cardholdergroup` (required): Cardholder group ID

**Description:** Gets log events for a specific cardholder group (longer version).

#### Log Event Report for Cardholders

**Endpoint:** `GET /api/events/cardholder/{cardholderid}`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Description:** Gets log events for specified cardholder (ordered by Time descending).

#### Log Event Report for a Door

**Endpoint:** `GET /api/events/door/{doorid}`

**Parameters:**
- `doorid` (required): Door ID

**Description:** Gets log events for specific door (ordered by Time descending).

#### Log Event Report for a Door Group

**Endpoint:** `GET /api/events/door-group/{doorgroupid}`

**Parameters:**
- `doorgroupid` (required): Door group ID

**Description:** Gets log events for specific door group (ordered by Time descending).

#### Log Event Report for a Site

**Endpoint:** `GET /api/events/site/{siteid}`

**Parameters:**
- `siteid` (required): Site ID

**Description:** Gets full-format log events for a site (ordered by Time descending).

#### Log Event Report for a Category

**Endpoint:** `GET /api/events/category/{category}`

**Parameters:**
- `category` (required): Event category number

**Valid Categories:**
- 1 = Alarm, 2 = Warning, 3 = Information, 4 = Normal, 5 = Access, 6 = Exit, 7 = Granted, 8 = Denied, 9 = Controller, 10 = Door, 11 = System, 12 = Camera, 13 = DVR, 14 = Video, 15 = Recording

**Description:** Gets full-format log events for specified category (ordered by Time descending).

#### Log Event Alarm Report

**Endpoint:** `GET /api/events/alarms`

**Query Parameters:**
- `siteid` (required): Site ID

**Description:** Gets most recent alarm log events for specified site (ordered by Time descending).

---

### Card Holders

#### Get Card Holders

**Endpoint:** `GET /api/cardholders`

**Query Parameters:**
- `siteid` (optional): Filter by site
- `customerid` (optional): Filter by customer

**Description:** Provides list of cardholders (ordered by last name).

#### Get Card Holder by Id

**Endpoint:** `GET /api/cardholders/{cardholderid}`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Description:** Returns individual cardholder details.

#### Get Card Holder by External Id

**Endpoint:** `GET /api/cardholders/external/{externalid}`

**Parameters:**
- `externalid` (required): External ID

**Description:** Returns cardholder by external ID.

#### Create Card Holder

**Endpoint:** `POST /api/cardholders`

**Request Body:**
```json
{
  "siteid": "integer",
  "customerid": "integer",
  "forename": "string",
  "surname": "string",
  "startValid": "dd/MM/yyyy HH:mm",
  "endValid": "dd/MM/yyyy HH:mm",
  "pin": "string",
  "cards": ["string"],
  "cardholderGroupId": "integer",
  "externalId": "string"
}
```

**Description:** Adds new cardholder at specified site.

**Notes:**
- siteid and customerid are compulsory
- Forename and Surname should be supplied
- StartValid and EndValid are optional (limit validity period)
- Card numbers must be unique
- Cards array allows maximum of 4 cards (takes precedence over Card1/Card2)
- One cardholder group per site + one all-sites level
- Returns new cardholder ID in response
- Wait 30 seconds before updating after creation

#### Update Card Holder

**Endpoint:** `PUT /api/cardholders/{cardholderid}`

**Description:** Updates existing cardholder (all fields updated).

**Notes:**
- Wait 30 seconds before updating after creation

#### Delete Card Holder

**Endpoint:** `DELETE /api/cardholders/{cardholderid}`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Description:** Deletes cardholder (disables card and removes from list).

#### Bulk Delete by Filter

**Endpoint:** `DELETE /api/cardholders`

**Query Parameters:**
- `customerID` (required): Customer ID
- Other filter parameters (optional)

**Description:** Deletes up to 100 cardholders matching parameters.

**Notes:**
- Date formats: "yyyy-MM-dd HH:mm", "yyyy-MM-dd HH:mm:ss", or "yyyy-MM-dd HH:mm:ss.fff"

#### Bulk Delete by IDs

**Endpoint:** `DELETE /api/cardholders/bulk`

**Request Body:**
```json
{
  "ids": ["integer"]
}
```

**Description:** Deletes up to 100 cardholders by ID list.

**Notes:**
- ItemResults shows success status per cardholder

#### Bulk Create Card Holders

**Endpoint:** `POST /api/cardholders/bulk`

**Request Body:**
```json
[
  {
    "siteid": "integer",
    "customerid": "integer",
    "forename": "string",
    "surname": "string",
    "startValid": "dd/MM/yyyy HH:mm",
    "endValid": "dd/MM/yyyy HH:mm",
    "pin": "string",
    "cards": ["string"]
  }
]
```

**Description:** Creates up to 100 new cardholders.

**Notes:**
- Returns ItemResults list with success flag and created ID for each
- Overall Success flag indicates if all were added successfully

#### Enable/Disable Card Holder

**Endpoint:** `POST /api/cardholders/{cardholderid}/enable` or `/disable`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Requires Location Headers:** May be required if customer requested additional security

**Description:** Enables or disables cardholder access rights.

#### Bulk Enable/Disable Card Holder

**Endpoint:** `POST /api/cardholders/enable` or `/disable`

**Request Body:**
```json
{
  "ids": ["integer"]
}
```

**Description:** Enables/disables multiple cardholders.

**Notes:**
- Returns sorted list with ItemResult success information

#### Get Random PIN

**Endpoint:** `GET /api/cardholders/randompin`

**Query Parameters:**
- `siteid` (required): Site ID
- `customerid` (required): Customer ID

**Description:** Returns a random PIN unique for the customer/site.

#### Switch Card Holder Site

**Endpoint:** `POST /api/cardholders/{cardholderid}/switchsite`

**Parameters:**
- `cardholderid` (required): Cardholder ID
- `newsiteid` (required): New site ID

**Description:** Moves cardholder to be managed by different site.

#### Set Card Holder Photograph

**Endpoint:** `POST /api/cardholders/{cardholderid}/photo`

**Parameters:**
- `cardholderid` (required): Cardholder ID
- Binary image file attachment

**Content-Type:** `multipart/form-data`

**Description:** Updates cardholder photograph.

#### Get Card Holder Photograph

**Endpoint:** `GET /api/cardholders/{cardholderid}/photo`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Description:** Retrieves cardholder photograph.

#### Get Card Holder Photograph Thumbnail

**Endpoint:** `GET /api/cardholders/{cardholderid}/photo/thumbnail`

**Parameters:**
- `cardholderid` (required): Cardholder ID

**Description:** Retrieves cardholder photograph thumbnail.

---

### Card Holder Groups

#### Get Card Holder Groups

**Endpoint:** `GET /api/cardholdersgroups`

**Query Parameters:**
- `customerid` (optional): Filter by customer
- `siteid` (optional): Filter by site

**Description:** Provides list of all cardholder groups.

**Notes:**
- MaxPinLength is read-only

#### Get Card Holder Group

**Endpoint:** `GET /api/cardholdersgroups/{cardholdergroupid}`

**Parameters:**
- `cardholdergroupid` (required): Cardholder group ID

**Description:** Returns individual cardholder group details.

#### Create Card Holder Group

**Endpoint:** `POST /api/cardholdersgroups`

**Request Body:**
```json
{
  "siteid": "integer",
  "customerid": "integer",
  "name": "string",
  "doorgroups": ["integer"],
  "timezones": ["integer"]
}
```

**Description:** Adds new cardholder group to site.

**Notes:**
- siteid and customerid are compulsory
- Timezones and door groups must be from same site or all-sites level
- Returns new ID in response
- Wait 30 seconds before updating after creation

#### Update Card Holder Group

**Endpoint:** `PUT /api/cardholdersgroups/{cardholdergroupid}`

**Description:** Updates existing cardholder group (all fields updated).

**Notes:**
- Wait 30 seconds before updating after creation

#### Delete Cardholder Group

**Endpoint:** `DELETE /api/cardholdersgroups/{cardholdergroupid}`

**Parameters:**
- `cardholdergroupid` (required): Cardholder group ID

**Description:** Deletes cardholder group (ID cannot be reused).

---

### Timezones

Timezones define time periods within which access can be granted/denied to cardholders.

#### Get All Timezones

**Endpoint:** `GET /api/timezones`

**Query Parameters:**
- `customerid` (optional): Filter by customer
- `siteid` (optional): Filter by site

**Description:** Provides list of all timezones.

**Default System Timezones:**
- "24 Hours": Provides access all day (system-managed, not editable)
- "No Timezone": Specifies no access (system-managed, not editable)

**Time Period Format:**
- Days of week (bit-mapped): Sunday=1, Monday=2, Tuesday=4, Wednesday=8, Thursday=16, Friday=32, Saturday=64
- Holiday types (bit-mapped): Type 1=1, Type 2=2, etc.
- Times: "HH:mm" format (00:00 to 23:59)
- Interpreted as local time by ACU

**Notes:**
- siteid of 0 specifies all-sites timezone (shareable across customer sites)

#### Get Timezone by Id

**Endpoint:** `GET /api/timezones/{timezoneid}`

**Parameters:**
- `timezoneid` (required): Timezone ID

**Description:** Returns individual timezone details (customers only).

#### Create Timezone

**Endpoint:** `POST /api/timezones`

**Request Body:**
```json
{
  "siteid": "integer",
  "customerid": "integer",
  "name": "string",
  "timePeriods": [
    {
      "startTime": "HH:mm",
      "endTime": "HH:mm",
      "daysOfWeek": "integer",
      "holidayTypes": "integer"
    }
  ]
}
```

**Description:** Adds new timezone to customer/site.

#### Update Timezone

**Endpoint:** `PUT /api/timezones/{timezoneid}`

**Description:** Updates existing timezone.

**Notes:**
- Wait 30 seconds before updating after creation

#### Delete Timezone

**Endpoint:** `DELETE /api/timezones/{timezoneid}`

**Parameters:**
- `timezoneid` (required): Timezone ID

**Description:** Deletes timezone.

**Restrictions:**
- Cannot delete if used by cardholder group
- Cannot delete if IsEditable=false

---

### WebHooks

WebHook support for log events (requires secret token in API Settings).

#### Register WebHook

**Endpoint:** `POST /api/webhooks`

**Request Body:**
```json
{
  "siteid": "integer",
  "customerid": "integer",
  "url": "string"
}
```

**Description:** Registers WebHook for Site or Customer.

**Notes:**
- One WebHook per Site + one for Customer
- Expires 5 minutes after user session expires
- Recommend registering after each login
- No Site ID = all customer events (ID starts with 'c' + customerID)
- With Site ID = site-specific events (ID starts with 's' + siteID)

#### Unregister WebHook

**Endpoint:** `DELETE /api/webhooks/{webhookid}`

**Parameters:**
- `webhookid` (required): WebHook ID

**Description:** Unregisters WebHook for Site or Customer.

#### Get WebHooks

**Endpoint:** `GET /api/webhooks`

**Query Parameters:**
- `customerid` (optional): Filter by customer
- `siteid` (optional): Filter by site

**Description:** Retrieves registered WebHooks.

---

### Video Diagnostics

#### Video Segmenter Service Data

**Endpoint:** `GET /api/video/segmenter`

**Description:** Captures diagnostic information about Segmenter server state.

**Response Fields:**
- `InstanceCount`: Number of active Azure instances
- `InstanceID`: Unique ID of each instance

#### Video Stream

**Endpoint:** `GET /api/video/stream`

**Query Parameters:**
- `instanceId` (optional): Stream instance ID

**Description:** Captures diagnostic information of video streams.

**Notes:**
- Source field: 0=Segmenter, 1=Player
- If instanceId passed, updates existing instance data
- If instanceId not passed, generates new instanceId in response

---

### Event Bookings

#### List All Sites

**Endpoint:** `GET /api2/Sites`

**Query Parameters:**
- `maxlimit` (optional): Maximum results
- `skipover` (optional): Skip records

**Description:** Lists available sites for a customer.

#### List All Doors on a Site

**Endpoint:** `GET /api2/Sites/{siteid}/Doors`

**Parameters:**
- `siteid` (required): Site ID

**Description:** Lists all doors on specified site.

#### Create Booking

**Endpoint:** `POST /api2/Bookings`

**Request Body:**
```json
{
  "siteid": "integer",
  "doorid": "integer",
  "pin": "string",
  "start": "dd/MM/yyyy HH:mm",
  "end": "dd/MM/yyyy HH:mm"
}
```

**Description:** Creates new event booking.

**Notes:**
- Date format must be exact: "dd/MM/yyyy HH:mm"
- Booking period should include buffer time before/after event
- Returns new bookingID in response

#### Get Booking

**Endpoint:** `GET /api2/Bookings/{bookingid}`

**Parameters:**
- `bookingid` (required): Booking ID

**Description:** Returns booking details (null if doesn't exist or access denied).

#### Update Booking

**Endpoint:** `PUT /api2/Bookings/{bookingid}`

**Request Body:**
```json
{
  "siteid": "integer",
  "doorid": "integer",
  "pin": "string",
  "card": "integer",
  "start": "dd/MM/yyyy HH:mm",
  "end": "dd/MM/yyyy HH:mm"
}
```

**Description:** Changes a booking (original deleted, new one created with new ID).

**Notes:**
- If card field is 0 or omitted, any linked card is deleted
- Wait 30 seconds before updating after creation

#### Delete Booking

**Endpoint:** `DELETE /api2/Bookings/{bookingid}`

**Parameters:**
- `bookingid` (required): Booking ID

**Description:** Removes booking from system.

#### Create Bulk Bookings

**Endpoint:** `POST /api2/Bookings/bulk`

**Request Body:**
```json
[
  {
    "siteid": "integer",
    "doorid": "integer",
    "pin": "string",
    "start": "dd/MM/yyyy HH:mm",
    "end": "dd/MM/yyyy HH:mm"
  }
]
```

**Description:** Creates multiple bookings.

**Notes:**
- Returns new bookingIDs in response

#### Delete Bookings by Customer Filter

**Endpoint:** `DELETE /api2/Bookings`

**Query Parameters:**
- `customerID` (required): Customer ID
- Other filter parameters (optional)

**Description:** Deletes up to 100 bookings matching parameters.

#### Delete Bookings by IDs

**Endpoint:** `DELETE /api2/Bookings/bulk`

**Request Body:**
```json
{
  "ids": ["integer"]
}
```

**Description:** Deletes up to 100 bookings by ID list.

**Notes:**
- ItemResults shows success per booking

#### Get All Bookings for a Site

**Endpoint:** `GET /api2/Sites/{siteid}/Bookings`

**Parameters:**
- `siteid` (required): Site ID

**Query Parameters:**
- `date` (optional): Start date "dd/MM/yyyy" (default: today)
- `maxlimit` (optional): Maximum results
- `skipover` (optional): Skip records

**Description:** Lists bookings for a site from specified date.

---

### Booking Output Scheduling

#### Set Schedule for Door Output

**Endpoint:** `POST /api2/Schedule`

**Request Body:**
```json
{
  "siteid": "integer",
  "doorid": "integer",
  "outputId": "integer",
  "schedulePeriods": [
    {
      "start": "dd/MM/yyyy HH:mm",
      "end": "dd/MM/yyyy HH:mm"
    }
  ]
}
```

**Description:** Applies schedule to trigger door output (Aux Relay or OP2/OP3).

**OutputId Values:**
- 1 = Aux Relay
- 2 = OP2
- 3 = OP3

**Schedule Rules:**
- Maximum 8 schedule periods per call
- One schedule active per output at a time
- Periods must be from current date, max 6 days future
- Pass empty array to turn output off
- If schedule spans 2 days, pass 2 separate periods
- Works on named day basis (repeats following week)

**Notes:**
- Date format must be exact: "dd/MM/yyyy HH:mm"

---

### Localisation

#### Get Localised Strings

**Endpoint:** `GET /api/localisation`

**Query Parameters:**
- `SearchPattern` (optional): Pattern to match identifiers
- `SearchStrings` (optional): Specific identifier list
- Language: Set via `Accept-Language` header

**Description:** Retrieves localised strings matching request criteria.

**Notes:**
- SearchPattern returns all matching identifier starts
- SearchStrings returns only exact matches
- SearchPattern takes precedence if both provided
- No parameters returns all resources

---

## Error Codes

| Code | Status | Detail |
|------|--------|--------|
| 1 | InvalidCustomer | The customer passed is invalid |
| 2 | InvalidSite | The site passed is invalid |
| 3 | InvalidData | Invalid input data provided |
| 4 | NoPermission | User does not have permission to this action |
| 5 | CardHolderDoesNotExist | Requested cardholder does not exist |
| 6 | TimezoneDoesNotExist | Requested time zone does not exist |
| 7 | DuplicateName | Cardholder with given name already exists |
| 8 | DuplicatePin | Provided PIN is already in use |
| 9 | PinRangeError | PIN is out of valid range |
| 10 | ZeroPinError | PIN of 0 is not valid |
| 11 | DuplicateCardError | Card number already in use |
| 12 | ValidityPeriodError | Validity period is invalid |
| 13 | DuplicateCHGError | Cardholder group with given name already exists |
| 14 | NoCHGError | No cardholder group provided |
| 15 | MaxCardsError | Exceeded maximum number of cards for cardholder |
| 16 | NameRequired | Cardholder must have a name |
| 18 | InvalidCardNumber | Invalid card number (range 0-4294967295) |

---

## Permissions

#### Get User Permissions

**Endpoint:** `GET /api/permissions`

**Description:** Gets list of access rights for current user (based on Auth header).

**Important:**
- Permission `AccessAllowed` is required to access customer/site entities
- If `AccessAllowed` = false, user cannot access any entities for that customer/site

---

## Important Notes

- **Token Validity:** 24 hours
- **Login Rate Limit:** 1 call per minute
- **Wait Time:** 30 seconds minimum between creation and update of entities
- **End of Life:** Apiary is being deprecated as of October 31, 2026
