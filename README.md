# ACT365

Minimal httpx based client for the [ACT365](https://www.act365.eu/) API.

API documentation: https://act365api.docs.apiary.io/#

Published pn PyPI: https://pypi.org/project/act365/

## API Coverage

The ACT365 API is much larger than what this library currently binds. The tables
below map the API surface to the Python bindings in `Act365Client` /
`Act365Auth` and the `act365` CLI.

### Covered

#### Authentication

| API | Binding | CLI |
| --- | --- | --- |
| `POST /api/account/login` | `Act365Auth` — automatic bearer-token login, re-login on 401, backoff on 429 | credentials via options or env vars |

#### Cardholders

| API | Binding | CLI |
| --- | --- | --- |
| List cardholders (`GET /api/cardholders`) | `Act365Client.getCardholders()` — paginated, supports `siteid`, `enabled`, `searchString` etc. filters | `act365 cardholders list` |
| Get cardholder by ID | `Act365Client.getCardholderById()` — client-side filter over the list endpoint, not the `GET /api/cardholders/{id}` endpoint | `act365 cardholders get --id` |
| Get cardholder by email | `Act365Client.getCardholderByEmail()` — client-side filter over the list endpoint | `act365 cardholders get --email` |
| Create cardholder (`POST /api/cardholders`) | `Act365Client.createCardholder()` | — |
| Update cardholder (`PUT /api/cardholders/{id}`) | `Act365Client.updateCardholder()` | — |

#### Event Bookings (`/api2`)

| API | Binding | CLI |
| --- | --- | --- |
| List booking sites (`GET /api2/Sites`) | `Act365Client.getBookingSites()` | — |
| List doors on a site (`GET /api2/Sites/{siteid}/Doors`) | `Act365Client.getBookingSiteDoors()` | — |
| Create booking (`POST /api2/Bookings`) | `Act365Client.createBooking()` | — |
| Get booking (`GET /api2/Bookings/{bookingid}`) | `Act365Client.getBooking()` | `act365 bookings get --id` |
| List bookings for a site (`GET /api2/Sites/{siteid}/Bookings`) | `Act365Client.getBookings()` | `act365 bookings list` |
| Delete booking (`DELETE /api2/Bookings/{bookingid}`) | `Act365Client.deleteBooking()` | `act365 bookings delete --id` / `--expired` |

`Act365Client` also exposes raw `post()` / `put()` / `delete()` passthroughs for
endpoints without dedicated bindings.

### Not Covered

No Python bindings exist yet for the following areas of the API:

- **Summary** — quick summary of customers/sites (`GET /api/summary`)
- **Customers** — list customers (`GET /api/customers`)
- **Sites** — list/get sites (`GET /api/sites`, `GET /api/sites/{siteid}`)
- **Site Lockdown** — activate / clear / command (`POST /api/lockdown/*`)
- **ACUs** — list, get, register, delete controllers (`/api/acus`)
- **Doors** — list, get, doors-for-cardholder, and door commands
  (Pass/Normalise/Lock/Unlock, single and bulk) (`/api/doors`)
- **Door Groups** — full CRUD (`/api/doorgroups`)
- **Cameras** — list cameras with live feed URLs (`GET /api/cameras`)
- **Reports / Events** — muster report, manual check-in/check-out, and all log
  event report variants (site, door, door group, cardholder, cardholder group,
  category, alarms) (`/api/events`)
- **Cardholders (remaining)** — get by external ID, delete, bulk create/delete,
  enable/disable (single and bulk), random PIN, switch site, and photo
  get/set/thumbnail
- **Cardholder Groups** — full CRUD (`/api/cardholdersgroups`)
- **Timezones** — full CRUD (`/api/timezones`)
- **WebHooks** — register, unregister, list (`/api/webhooks`)
- **Video Diagnostics** — segmenter and stream diagnostics (`/api/video/*`)
- **Event Bookings (remaining)** — update booking, bulk create, delete by
  filter, bulk delete by IDs
- **Booking Output Scheduling** — door output schedules (`POST /api2/Schedule`)
- **Localisation** — localised strings (`GET /api/localisation`)
- **Permissions** — current user access rights (`GET /api/permissions`)
