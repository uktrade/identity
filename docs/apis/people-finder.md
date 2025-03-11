# People Finder

> This API is available at `/api/peoplefinder/`

The ID service exposes an API that provides read and edit functionality designed for the PeopleFinder / Intranet integration.

### API Endpoints

#### Get Profile:
`/person/<slug>` : returns a minimal peoplefinder profile record
#### Update Profile:
`/person/<slug>` : updates an existing people finder profile and returns a full people finder profile as response
#### Create Profile:
`/person` : creates a new people finder profile and returns a full people finder profile as response


#### Reference data can be accessed via `/api/peoplefinder/reference/<endpoint>`. Here is the list of reference endpoints:

- `countries` : lists all countries from the database
- `uk_staff_locations` : lists all uk staff locations from the database
- `remote_working` : lists remote working options
- `workdays` : lists workday options
- `learning_interests` : lists learning interests
- `professions` : lists professions
- `grades` : list of grades

